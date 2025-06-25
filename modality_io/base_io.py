# modality_io/base_io.py
from abc import ABC, abstractmethod
from typing import Any, List
from pathlib import Path


class IORegistry:
    """
    Global registry to keep track of modality-specific IO classes.
    """
    readers = {}
    writers = {}

    @classmethod
    def register_reader(cls, modality: str, reader_cls):
        cls.readers[modality] = reader_cls

    @classmethod
    def register_writer(cls, modality: str, writer_cls):
        cls.writers[modality] = writer_cls

    @classmethod
    def get_reader(cls, modality: str):
        return cls.readers.get(modality)

    @classmethod
    def get_writer(cls, modality: str):
        return cls.writers.get(modality)


class BaseReader(ABC):
    @abstractmethod
    def read(self, file_path: str) -> Any:
        """
        Reads raw sensor data from a file.
        """
        pass

    @staticmethod
    def validate_extension(file_ext: str, supported_extensions: List) -> bool:
        """
        Validates if the file extension is readable.
        """
        if not file_ext:
            return False
        return file_ext.lower() in {ext.lower() for ext in supported_extensions}


class BaseWriter(ABC):
    supported_extensions: List[str] = []

    @abstractmethod
    def write(self, data: Any, file_path: str) -> None:
        """
        Writes sensor data to a file.
        """
        pass

    @staticmethod
    def validate_extension(file_ext: str, supported_extensions: List) -> bool:
        """
        Validates if the file extension is writable.
        """
        if not file_ext:
            return False
        return file_ext.lower() in {ext.lower() for ext in supported_extensions}


class BaseIO(BaseReader, BaseWriter):
    """
    Unified base class for modalities that support both reading and writing.
    """

    @abstractmethod
    def read(self, file_path: str) -> Any:
        pass

    @abstractmethod
    def write(self, data: Any, file_path: str) -> None:
        pass

    def _validate_file_extension(self, file_path: str, supported_extensions: List[str]) -> None:
        if not self.validate_extension(Path(file_path).suffix, supported_extensions):
            raise ValueError(f"Unsupported file extension: {file_path}")
