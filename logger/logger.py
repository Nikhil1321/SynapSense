import logging
import logging.handlers
import datetime
import secrets
import re
import sys
import warnings
from typing import Optional
from utils.path_manager import get_logging_path
from logger.logger_config import LOGGER_SETTINGS


def sanitize_filename(name: str) -> str:
    """
    Sanitizes a filename by replacing spaces with underscores and removing unsafe characters.
    """
    name = name.strip().replace(' ', '_')
    name = re.sub(r'[^\w\-\.]', '', name)  # Allow alphanumerics, underscores, dash, dot
    return name


def validate_mode(mode: str) -> str:
    """
    Validates and standardizes the logging mode.
    """
    supported_modes = LOGGER_SETTINGS['available_modes']
    if mode.lower() not in supported_modes:
        raise ValueError(f"Invalid logging mode '{mode}'. Supported modes: {supported_modes}.")
    return mode.lower()


def get_backup_count(mode: str) -> int:
    """
    Returns dynamic backup counts based on logging mode.
    """
    mode = mode.lower()
    return {
        'development': LOGGER_SETTINGS['backup_counts']['development'],
        'debug': LOGGER_SETTINGS['backup_counts']['debug'],
        'experiment': LOGGER_SETTINGS['backup_counts']['experiment'],
        'benchmark': LOGGER_SETTINGS['backup_counts']['benchmark'],
        'test': LOGGER_SETTINGS['backup_counts']['test']
    }.get(mode, 5)  # Default to 5 backups if mode is not recognized


def get_logger(name: str = LOGGER_SETTINGS['name'],
               experiment_name: Optional[str] = LOGGER_SETTINGS['experiment_name'],
               log_level: int = LOGGER_SETTINGS['log_level'],
               mode: str = LOGGER_SETTINGS['default_mode'],
               stream_only: bool = LOGGER_SETTINGS['stream_only'],
               log_file_name: Optional[str] = LOGGER_SETTINGS['log_file_name']) -> logging.Logger:
    """
    Creates a size-based rotating logger with experiment-aware, salted, timestamped log file names.

    Args:
        name (str): Logger name.
        experiment_name (Optional[str]): Experiment identifier.
        log_level (int): Logging level.
        mode (str): Logging mode: 'development', 'debug', 'experiment', 'benchmark', 'test'
        stream_only (bool): If True, disables file logging.
        log_file_name (Optional[str]): Optional static log file name.

    Returns:
        logging.Logger: Configured logger object.
    """
    logger = logging.getLogger(name)

    if logger.hasHandlers():
        return logger  # Prevent duplicate handlers

    logger.setLevel(log_level)

    mode = validate_mode(mode)
    backup_count = get_backup_count(mode)

    logger_label = sanitize_filename(name)
    experiment_label = sanitize_filename(experiment_name or 'general')

    formatter = logging.Formatter(
        fmt='[%(asctime)s] [%(name)s] [%(levelname)s] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console Handler
    console_handler = logging.StreamHandler()
    if mode == 'development':
        console_handler.setLevel(logging.INFO)
    elif mode == 'debug':
        console_handler.setLevel(logging.DEBUG)
    elif mode in {'experiment', 'benchmark'}:
        console_handler.setLevel(logging.INFO)
    elif mode == 'test':
        console_handler.setLevel(logging.WARNING)

    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if not stream_only:
        try:
            if log_file_name is None:
                now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                salt = secrets.token_hex(3)
                log_file_name = f"{logger_label}_{experiment_label}_{mode}_{now}_{salt}.log"
            else:
                log_file_name = sanitize_filename(log_file_name)

            log_path = get_logging_path(mode=mode)
            log_file = log_path / log_file_name
            log_file.parent.mkdir(parents=True, exist_ok=True)

            # Size-based Rotating File Handler
            file_handler = logging.handlers.RotatingFileHandler(
                filename=str(log_file),
                maxBytes=LOGGER_SETTINGS['max_bytes'],
                backupCount=backup_count,
                encoding=LOGGER_SETTINGS['encoding']
            )

            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        except Exception as e:
            logger.warning(f"[LOGGER ERROR] Failed to initialize file handler: {e}")
            # Fallback: Console logging will continue without crashing

    # Setup global exception and warning capture
    def log_uncaught_exceptions(exc_type, exc_value, exc_traceback):
        """
        Logs uncaught exceptions using the configured logger.
        """
        if issubclass(exc_type, KeyboardInterrupt):
            # Let KeyboardInterrupt exit normally
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        # logger.critical("Uncaught exception:", exc_info=(exc_type, exc_value, exc_traceback))
        logger.error(f"Uncaught {exc_type.__name__}: {exc_value}", exc_info=(exc_type, exc_value, exc_traceback))

    def capture_warnings(message, category, filename, lineno, file=None, line=None):
        """
        Redirects warnings to the logger.
        """
        logger.warning(f"{category.__name__}: {message} ({filename}:{lineno})")

    # Register the global exception hook
    sys.excepthook = log_uncaught_exceptions

    # Redirect warnings to the logger
    logging.captureWarnings(True)
    warnings.showwarning = capture_warnings

    return logger
