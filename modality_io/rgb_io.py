# modality_io/rgb.py

from modality_io.base_io import BaseIO, IORegistry
from modality_io.utils import validate_extension, get_file_extension, ensure_directory_exists
from typing import Any, Dict
from pathlib import Path
import cv2
import numpy as np
from configs.modality_config import SUPPORTED_EXTENSIONS
from logger.logger_manager import LoggerManager

# Initialize logger
log = LoggerManager.get_logger()


class RGBImageIO(BaseIO):
    def __init__(self):
        self.supported_read_extensions = SUPPORTED_EXTENSIONS['rgb']['read']
        self.supported_write_extensions = SUPPORTED_EXTENSIONS['rgb']['write']

        # IORegistry.register_reader('rgb', self.__class__)
        # IORegistry.register_writer('rgb', self.__class__)

    def read(self, file_path: str) -> Dict[str, Any]:
        file_ext = get_file_extension(file_path)
        if not validate_extension(file_path, self.supported_read_extensions):
            raise ValueError(f"Unsupported file extension for RGB: {file_ext}")

        image = cv2.imread(file_path, cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError(f"Failed to read image: {file_path}")

        # Convert BGR to RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        log.info(f"RGB image successfully read: {file_path} | Shape: {image.shape}")

        return {
            'data': image,
            'timestamps': None,  # RGB images typically don't have timestamps
            'columns': ['R', 'G', 'B']  # Generic channel names
        }

    def write(self, data_bundle: Dict[str, Any], file_path: str) -> None:
        file_ext = get_file_extension(file_path)
        if not validate_extension(file_path, self.supported_write_extensions):
            raise ValueError(f"Unsupported file extension for RGB: {file_ext}")

        if 'data' not in data_bundle or data_bundle['data'] is None:
            raise ValueError("Data bundle must contain 'data' key with valid image data.")

        data = data_bundle['data']

        if not isinstance(data, np.ndarray):
            raise ValueError("RGB data must be a NumPy array.")

        ensure_directory_exists(str(Path(file_path).parent))

        # Convert RGB to BGR for OpenCV writing
        data_bgr = cv2.cvtColor(data, cv2.COLOR_RGB2BGR)
        cv2.imwrite(file_path, data_bgr)

        log.info(f"RGB image successfully saved: {file_path} | Shape: {data.shape}")


IORegistry.register_reader('rgb', RGBImageIO)
IORegistry.register_writer('rgb', RGBImageIO)
