# modality_io/imu_io.py

from modality_io.base_io import BaseIO, IORegistry
from typing import Any, Optional, Tuple
from pathlib import Path
import numpy as np
import pandas as pd
from configs.modality_config import SUPPORTED_EXTENSIONS
from logger.logger_manager import LoggerManager

# Initialise logger
log = LoggerManager.get_logger()


class IMUIO(BaseIO):
    def __init__(self):
        self.data: Optional[np.ndarray] = None
        self.columns: Optional[list] = None
        self.timestamps: Optional[np.ndarray] = None
        self.supported_read_extensions = SUPPORTED_EXTENSIONS['imu']['read']
        self.supported_write_extensions = SUPPORTED_EXTENSIONS['imu']['write']

        IORegistry.register_reader('imu', self.__class__)
        IORegistry.register_writer('imu', self.__class__)

    def read(self, file_path: str) -> np.ndarray:
        if not self.validate_extension(Path(file_path).suffix, self.supported_read_extensions):
            raise ValueError(f"Unsupported file extension for IMUIO: {file_path}")

        ext = Path(file_path).suffix.lower()

        try:
            if ext == '.csv':
                df = pd.read_csv(file_path, low_memory=False)
            elif ext == '.txt':
                df = pd.read_csv(file_path, delimiter=r'\s+', low_memory=False)
            else:
                raise ValueError(f"Unsupported file format: {ext}")

            available_columns = set(df.columns.str.lower())

            # Define flexible field patterns
            gyro_fields = {'gyro_x', 'gyro_y', 'gyro_z'}
            accel_fields = {'accel_x', 'accel_y', 'accel_z', 'x', 'y', 'z'}
            time_fields = {'timestamp', 'time', 'datetime'}

            sensor_fields = []

            gyro_candidates = [col for col in df.columns if col.lower() in gyro_fields]
            accel_candidates = [col for col in df.columns if col.lower() in accel_fields]
            time_candidates = [col for col in df.columns if col.lower() in time_fields]

            if gyro_candidates:
                sensor_fields.extend(gyro_candidates)
                log.info(f"Gyroscope data found: {gyro_candidates}")

            if accel_candidates:
                sensor_fields.extend(accel_candidates)
                log.info(f"Accelerometer or generic axis data found: {accel_candidates}")

            if not sensor_fields:
                raise ValueError("No valid IMU sensor data found in file.")

            if time_candidates:
                timestamp_column = time_candidates[0]
                self.timestamps = df[timestamp_column].to_numpy()
                log.info(f"Timestamp column found: {timestamp_column}")

                combined_data = np.column_stack((self.timestamps.reshape(-1, 1), df[sensor_fields].to_numpy(dtype=np.float32)))
                self.columns = [timestamp_column] + sensor_fields
                self.data = combined_data
            else:
                self.timestamps = None
                self.data = df[sensor_fields].to_numpy(dtype=np.float32)
                self.columns = sensor_fields
                log.info("No timestamp column found.")

        except Exception as e:
            raise ValueError(f"Failed to read IMU file {file_path}: {e}")

        log.info(f"IMU file successfully read: {file_path} | Shape: {self.data.shape} | Columns: {self.columns}")
        return self.data

    def write(self, data: Any = None, file_path: str = None, columns: Optional[list] = None, timestamps: Optional[np.ndarray] = None) -> None:
        if file_path is None:
            raise ValueError("file_path must be provided for writing.")

        if data is None:
            if self.data is None:
                raise ValueError("No IMU data loaded to write.")
            data = self.data

        if not isinstance(data, np.ndarray):
            raise ValueError("IMU data must be a NumPy array.")

        if not self.validate_extension(Path(file_path).suffix, self.supported_write_extensions):
            raise ValueError(f"Unsupported file extension for IMUIO: {file_path}")

        try:
            if columns is None:
                if self.columns is not None:
                    columns = self.columns
                else:
                    columns = [f'col_{i}' for i in range(data.shape[1])]

            df = pd.DataFrame(data, columns=columns)
            df.to_csv(file_path, index=False)

        except Exception as e:
            raise ValueError(f"Failed to write IMU file {file_path}: {e}")

        log.info(f"IMU file successfully saved: {file_path} | Shape: {data.shape} | Columns: {columns}")
