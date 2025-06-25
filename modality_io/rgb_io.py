# modality_io/rgb_io.py
from modality_io.base_io import BaseIO, IORegistry
from typing import Any, Optional
from pathlib import Path
import cv2
import numpy as np
from configs.modality_config import SUPPORTED_EXTENSIONS
from logger.logger_manager import LoggerManager

# Initialise logger
log = LoggerManager.get_logger()


class RGBImageIO(BaseIO):
    def __init__(self):
        self.image: Optional[np.ndarray] = None
        self.supported_read_extensions = SUPPORTED_EXTENSIONS['rgb']['read']
        self.supported_write_extensions = SUPPORTED_EXTENSIONS['rgb']['write']

        IORegistry.register_reader('rgb', self.__class__)
        IORegistry.register_writer('rgb', self.__class__)

    def read(self, file_path: str) -> np.ndarray:
        if not self.validate_extension(Path(file_path).suffix, self.supported_read_extensions):
            raise ValueError(f"Unsupported file extension for RGBIO: {file_path}")

        self.image = cv2.imread(file_path, cv2.IMREAD_COLOR)
        if self.image is None:
            raise ValueError(f"Failed to read image: {file_path}")

        # Convert BGR to RGB
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        return self.image

    def write(self, data: Any = None, file_path: str = None) -> None:
        if file_path is None:
            raise ValueError("file_path must be provided for writing.")

        if data is None:
            if self.image is None:
                raise ValueError("No image loaded to write.")
            data = self.image

        if not self.validate_extension(Path(file_path).suffix, self.supported_write_extensions):
            raise ValueError(f"Unsupported file extension for RGBIO: {file_path}")

        # Convert RGB to BGR for OpenCV writing
        data_bgr = cv2.cvtColor(data, cv2.COLOR_RGB2BGR)
        cv2.imwrite(file_path, data_bgr)
        log.info(f"Image saved to {file_path}")
