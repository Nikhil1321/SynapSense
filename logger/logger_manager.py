# utils/logger_manager.py
from typing import Optional
from logger.logger import get_logger
from logger.logger_config import LOGGER_SETTINGS


class LoggerManager:
    """
    Project-wide logger wrapper that ensures a single logger instance across the project.
    """
    _logger_instance = None
    _init_params = {}

    @classmethod
    def initialize_logger(cls, name: str = LOGGER_SETTINGS['name'],
                          experiment_name: Optional[str] = LOGGER_SETTINGS['experiment_name'],
                          log_level: int = LOGGER_SETTINGS['log_level'],
                          mode: str = LOGGER_SETTINGS['default_mode'],
                          stream_only: bool = LOGGER_SETTINGS['stream_only'],
                          log_file_name: Optional[str] = LOGGER_SETTINGS['log_file_name']):
        if cls._logger_instance is None:
            cls._logger_instance = get_logger(
                name=name,
                experiment_name=experiment_name,
                mode=mode,
                log_level=log_level,
                stream_only=stream_only,
                log_file_name=log_file_name
            )
            cls._init_params = {
                'name': name,
                'experiment_name': experiment_name,
                'mode': mode,
                'log_level': log_level,
                'stream_only': stream_only,
                'log_file_name': log_file_name
            }

    @classmethod
    def get_logger(cls):
        if cls._logger_instance is None:
            print("[LOGGER INFO] Logger not initialized. Auto-initializing with default settings.")
            cls.initialize_logger()
        return cls._logger_instance

    @classmethod
    def reinitialize_logger(cls):
        """
        Reinitializes the logger with the originally provided parameters.
        """
        if not cls._init_params:
            raise RuntimeError("Logger was never initialized. Cannot reinitialize.")
        cls._logger_instance = get_logger(
            name=cls._init_params['name'],
            experiment_name=cls._init_params['experiment_name'],
            mode=cls._init_params['mode']
        )

    @classmethod
    def shutdown_logger(cls):
        """
        Gracefully shuts down all active loggers and clears the singleton instance.
        """
        if cls._logger_instance:
            logger = cls._logger_instance
            handlers = logger.handlers[:]
            for handler in handlers:
                try:
                    handler.close()
                    logger.removeHandler(handler)
                except Exception as e:
                    print(f"[LOGGER WARNING] Failed to close handler: {e}")
            cls._logger_instance = None
