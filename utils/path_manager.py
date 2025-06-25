import warnings
from pathlib import Path
from typing import Optional

from configs.dataset_config import PROJECT_ROOT, DATASET_DIRS
from logger.logger_config import LOG_PATH_ROOT, LOG_DIR


def get_dataset_path(dataset_name, modality=None):
    if dataset_name not in DATASET_DIRS:
        raise ValueError(f"Dataset '{dataset_name}' not found in configured datasets.")

    dataset_root_dir = DATASET_DIRS[dataset_name]['root']
    dataset_root = PROJECT_ROOT / 'data' / dataset_root_dir

    if modality:
        modality_dirs = DATASET_DIRS[dataset_name]
        if modality not in modality_dirs:
            raise ValueError(f"Modality '{modality}' not found for dataset '{dataset_name}'.")
        return dataset_root / modality_dirs[modality]

    return dataset_root


def get_logging_path(root: Path = LOG_PATH_ROOT, mode: Optional[str] = None) -> Path:
    """
    Returns the log path for the given mode. If no mode is provided, logs are saved to the root directory with a
    warning.

    Args:
        root (Path): The root logs directory.
        mode (str): Logging mode (e.g., 'development', 'debug', 'experiment', 'benchmark', 'test').

    Returns:
        Path: Full log directory path.
    """
    if mode is None:
        warnings.warn(
            "No logging mode selected. Log files will be saved in the root logs directory.",
            category=UserWarning
        )
        root.mkdir(parents=True, exist_ok=True)
        return root

    if mode not in LOG_DIR:
        raise ValueError(f"Invalid logging mode '{mode}'. Supported modes: {list(LOG_DIR.keys())}")

    log_path = root / LOG_DIR[mode]
    log_path.mkdir(parents=True, exist_ok=True)
    return log_path
