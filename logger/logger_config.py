from pathlib import Path
import logging

# Project root path
PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent

# Log root directory
LOG_PATH_ROOT: Path = PROJECT_ROOT / 'logs'

# Supported logging subdirectories
LOG_DIR = {
    'debug': 'debug',
    'experiment': 'experiment',
    'benchmark': 'benchmark',
    'test': 'test'
}

LOGGER_SETTINGS = {
    'name': 'Project SynapSense',
    'experiment_name': 'generic run',
    'log_level': logging.DEBUG,
    'available_modes': {'development', 'debug', 'experiment', 'benchmark', 'test'},
    'default_mode': 'debug',
    'stream_only': False,
    'log_file_name': None,
    'max_bytes': 10 * 1024 * 1024,  # 10 MB
    'backup_counts': {
        'development': 3,
        'debug': 7,
        'experiment': 10,
        'benchmark': 5,
        'test': 2
    },
    'encoding': 'utf8'
}

LOG_DELETION_PARAMS = {
    'target_dir': '',
    'mode': 'full',     # Available modes 'full', 'files', 'retain_last_n'
    'retain_last_n': 3,
    'file_extension': '*.log',
    'filter_keywords': None,
    'compress': False,
    'requires_logger_shutdown': False
}
