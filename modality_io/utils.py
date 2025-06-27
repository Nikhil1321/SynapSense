# modality_io/common.py

import os
from pathlib import Path
from typing import List, Optional
from configs.modality_config import SUPPORTED_EXTENSIONS


def validate_extension(file_path: str, supported_extensions: List[str]) -> bool:
    """
    Checks if the file extension is supported.
    """
    return Path(file_path).suffix.lower() in {ext.lower() for ext in supported_extensions}


def get_file_extension(file_path: str) -> str:
    """
    Extracts the file extension from the file path.
    """
    return Path(file_path).suffix.lower()


def get_file_size(file_path: str) -> str:
    """
    Returns the file size in a human-readable format (Bytes, KB, MB, GB).
    """
    size_bytes = os.path.getsize(file_path)

    if size_bytes < 1024:
        return f"{size_bytes} Bytes"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / (1024 ** 2):.2f} MB"
    else:
        return f"{size_bytes / (1024 ** 3):.2f} GB"


def is_valid_file(file_path: str, allowed_extensions: List[str]) -> bool:
    """
    Checks if a file exists and has a valid extension.
    """
    if not os.path.isfile(file_path):
        return False
    ext = get_file_extension(file_path)
    return ext in [e.lower() for e in allowed_extensions]


def ensure_directory_exists(directory_path: str) -> None:
    """
    Ensures that a directory exists, creates it if it does not.
    """
    Path(directory_path).mkdir(parents=True, exist_ok=True)


def list_files_with_extensions(directory_path: str, allowed_extensions: List[str]) -> List[str]:
    """
    Lists all files in a directory and its subdirectories with the specified extensions.
    """
    directory = Path(directory_path)
    files = []
    for ext in allowed_extensions:
        files.extend(directory.rglob(f'*{ext}'))
    return [str(f) for f in files if f.is_file()]


def resolve_modality_from_extension(file_path: str, operation: str = 'read') -> Optional[str]:
    """
    Resolves the modality based on the file extension and operation type.
    """
    ext = get_file_extension(file_path)

    for modality, ops in SUPPORTED_EXTENSIONS.items():
        if ext in [e.lower() for e in ops[operation]]:
            return modality
    return None


def list_supported_files(directory_path: str, modality: str, operation: str = 'read') -> List[str]:
    """
    Lists all supported files for a given modality and operation in a directory.
    """
    if modality not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Modality '{modality}' is not configured in SUPPORTED_EXTENSIONS.")

    if operation not in ['read', 'write']:
        raise ValueError(f"Operation '{operation}' is invalid. Use 'read' or 'write'.")

    allowed_extensions = SUPPORTED_EXTENSIONS[modality][operation]
    return list_files_with_extensions(directory_path, allowed_extensions)


def is_supported_file(file_path: str, modality: str, operation: str = 'read') -> bool:
    """
    Checks if the file is supported for a specific modality and operation.
    """
    if modality not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Modality '{modality}' is not configured in SUPPORTED_EXTENSIONS.")

    if operation not in ['read', 'write']:
        raise ValueError(f"Operation '{operation}' is invalid. Use 'read' or 'write'.")

    allowed_extensions = SUPPORTED_EXTENSIONS[modality][operation]
    return is_valid_file(file_path, allowed_extensions)


def get_global_supported_extensions(operation: str, supported_extensions: dict = SUPPORTED_EXTENSIONS) -> List[str]:
    """
    Combines extensions for a specific operation ('read' or 'write') across all modalities.

    Args:
        supported_extensions (dict): Modality-specific supported extensions.
        operation (str): Operation type ('read' or 'write').

    Returns:
        List[str]: Sorted list of combined unique extensions for the specified operation.
    """
    if operation not in {'read', 'write'}:
        raise ValueError("Operation must be 'read' or 'write'.")

    combined = set()

    for modality_extensions in supported_extensions.values():
        combined.update(modality_extensions.get(operation, []))

    return sorted(combined)
