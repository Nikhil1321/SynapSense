import importlib
import pkgutil
from modality_io import __path__ as modality_path
from modality_io.base_io import IORegistry
from modality_io.utils import resolve_modality_from_extension, validate_extension
from logger.logger_manager import LoggerManager

log = LoggerManager.get_logger()

# Force dynamic loading of all modality classes
__all__ = []

for loader, module_name, is_pkg in pkgutil.iter_modules(modality_path):
    if module_name not in ['base_io', 'utils', 'facade']:
        importlib.import_module(f"modality_io.{module_name}")
        __all__.append(module_name)


class ModalityIO:
    """
    Facade class providing a unified interface for reading and writing sensor data across all modalities.
    """

    def __init__(self):
        pass

    def read(self, file_path: str) -> dict:
        modality = resolve_modality_from_extension(file_path, operation='read')
        if modality is None:
            raise ValueError(f"Unsupported file extension: {file_path}")

        reader_cls = IORegistry.get_reader(modality)
        if reader_cls is None:
            raise ValueError(f"No reader registered for modality: {modality}")

        reader = reader_cls()
        log.info(f"Reading {modality.upper()} data from {file_path}")
        return reader.read(file_path)

    def write(self, modality: str, data_bundle: dict, file_path: str) -> None:
        writer_cls = IORegistry.get_writer(modality)
        if writer_cls is None:
            raise ValueError(f"No writer registered for modality: {modality}")

        writer = writer_cls()
        log.info(f"Writing {modality.upper()} data to {file_path}")
        writer.write(data_bundle, file_path)

    def read_with_modality(self, modality: str, file_path: str) -> dict:
        reader_cls = IORegistry.get_reader(modality)
        if reader_cls is None:
            raise ValueError(f"No reader registered for modality: {modality}")

        reader = reader_cls()
        log.info(f"Reading {modality.upper()} data from {file_path} with forced modality override")
        return reader.read(file_path)

    def validate_file_for_modality(self, modality: str, file_path: str, operation: str = 'read') -> bool:
        from configs.modality_config import SUPPORTED_EXTENSIONS
        allowed_extensions = SUPPORTED_EXTENSIONS[modality][operation]
        return validate_extension(file_path, allowed_extensions)
