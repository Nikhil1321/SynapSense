import os
from pathlib import Path
from typing import List
from configs.modality_config import SUPPORTED_EXTENSIONS


def is_valid_file(file_path: str, allowed_extensions: List[str]) -> bool:
    """
    Checks if a file exists and has a valid extension.
    """
    if not os.path.isfile(file_path):
        return False

    ext = os.path.splitext(file_path)[1].lower()
    return ext in [e.lower() for e in allowed_extensions]


def ensure_directory_exists(directory_path: str) -> None:
    """
    Ensures that a directory exists. Creates it if it does not.
    """
    Path(directory_path).mkdir(parents=True, exist_ok=True)


def list_files_with_extensions(directory_path: str, allowed_extensions: List[str]) -> List[str]:
    """
    Lists all files in a directory and its subdirectories with specified extensions.
    """
    directory = Path(directory_path)
    files = []
    for ext in allowed_extensions:
        files.extend(directory.rglob(f'*{ext}'))
    return [str(f) for f in files if f.is_file()]


def get_file_extension(file_path: str) -> str:
    """
    Extracts the file extension from a file path.
    """
    return os.path.splitext(file_path)[1].lower()


def get_file_size(file_path: str) -> float:
    """
    Gets the file size in megabytes.
    """
    return os.path.getsize(file_path) / (1024 * 1024)


def is_supported_file(file_path: str, modality: str, operation: str = 'read') -> bool:
    """
    Checks if a file is supported for a specific modality and operation (read/write).

    Args:
        file_path (str): Path to the file.
        modality (str): One of 'DVS', 'LiDAR', 'IMU', 'RGB'.
        operation (str): 'read' or 'write'

    Returns:
        bool: True if file extension is supported for the modality and operation.
    """
    if modality not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Modality '{modality}' is not configured in SUPPORTED_EXTENSIONS.")

    if operation not in ['read', 'write']:
        raise ValueError(f"Operation '{operation}' is invalid. Use 'read' or 'write'.")

    allowed_extensions = SUPPORTED_EXTENSIONS[modality][operation]
    return is_valid_file(file_path, allowed_extensions)


def list_supported_files(directory_path: str, modality: str, operation: str = 'read') -> List[str]:
    """
    Lists files in a directory (recursively) supported for a given modality and operation.

    Args:
        directory_path (str): Directory to search.
        modality (str): 'DVS', 'LiDAR', 'IMU', 'RGB'
        operation (str): 'read' or 'write'

    Returns:
        List[str]: List of valid files.
    """
    if modality not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Modality '{modality}' is not configured in SUPPORTED_EXTENSIONS.")

    if operation not in ['read', 'write']:
        raise ValueError(f"Operation '{operation}' is invalid. Use 'read' or 'write'.")

    allowed_extensions = SUPPORTED_EXTENSIONS[modality][operation]
    return list_files_with_extensions(directory_path, allowed_extensions)
