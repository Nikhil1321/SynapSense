# modality_io/base_io.py

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Type
from pathlib import Path


class IORegistry:
    """
    Global registry to manage modality-specific IO classes.
    """
    readers: dict[str, Type['BaseIO']] = {}
    writers: dict[str, Type['BaseIO']] = {}

    @classmethod
    def register_reader(cls, modality: str, reader_cls: Type['BaseIO']) -> None:
        cls.readers[modality] = reader_cls

    @classmethod
    def register_writer(cls, modality: str, writer_cls: Type['BaseIO']) -> None:
        cls.writers[modality] = writer_cls

    @classmethod
    def get_reader(cls, modality: str) -> Type['BaseIO']:
        return cls.readers.get(modality)

    @classmethod
    def get_writer(cls, modality: str) -> Type['BaseIO']:
        return cls.writers.get(modality)


class BaseIO(ABC):
    """
    Abstract base class enforcing a standardized I/O interface for all modalities.
    Each method must handle file validation and use standardized data bundles.
    """

    @abstractmethod
    def read(self, file_path: str) -> Dict[str, Any]:
        """
        Reads sensor data from the specified file.

        Args:
            file_path (str): Path to the file.

        Returns:
            dict: {
                'data': np.ndarray,
                'timestamps': Optional[np.ndarray],
                'columns': Optional[List[str]]
            }
        """
        pass

    @abstractmethod
    def write(self, data_bundle: Dict[str, Any], file_path: str) -> None:
        """
        Writes sensor data to the specified file.

        Args:
            data_bundle (dict): Must contain 'data'. Optionally contains 'timestamps' and 'columns'.
            file_path (str): Path to the output file.
        """
        pass

    @staticmethod
    def validate_extension(file_ext: str, supported_extensions: List[str]) -> bool:
        """
        Checks if a file extension is within the list of supported extensions.

        Args:
            file_ext (str): File extension.
            supported_extensions (List[str]): List of allowed extensions.

        Returns:
            bool: True if valid, False otherwise.
        """
        if not file_ext:
            return False
        return file_ext.lower() in {ext.lower() for ext in supported_extensions}

    @staticmethod
    def validate_or_raise_extension(file_path: str, supported_extensions: List[str]) -> None:
        """
        Validates file extension and raises an error if unsupported.

        Args:
            file_path (str): File path to validate.
            supported_extensions (List[str]): List of allowed extensions.

        Raises:
            ValueError: If file extension is unsupported.
        """
        if not BaseIO.validate_extension(Path(file_path).suffix, supported_extensions):
            raise ValueError(f"Unsupported file extension: {file_path}")
