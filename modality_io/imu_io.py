# modality_io/imu.py

from modality_io.base_io import BaseIO, IORegistry
from modality_io.utils import validate_extension, get_file_extension, ensure_directory_exists
from typing import Any, Dict, List
from pathlib import Path
import numpy as np
import pandas as pd
from configs.modality_config import SUPPORTED_EXTENSIONS
from logger.logger_manager import LoggerManager

# Initialize logger
log = LoggerManager.get_logger()


class IMUIO(BaseIO):
    def __init__(self):
        self.supported_read_extensions = SUPPORTED_EXTENSIONS['imu']['read']
        self.supported_write_extensions = SUPPORTED_EXTENSIONS['imu']['write']

        # IORegistry.register_reader('imu', self.__class__)
        # IORegistry.register_writer('imu', self.__class__)

    def read(self, file_path: str) -> Dict[str, Any]:
        file_ext = get_file_extension(file_path)
        if not validate_extension(file_path, self.supported_read_extensions):
            raise ValueError(f"Unsupported file extension for IMU: {file_ext}")

        try:
            if file_ext == '.csv':
                df = pd.read_csv(file_path, low_memory=False)
            elif file_ext == '.txt':
                df = pd.read_csv(file_path, delimiter=r'\s+', low_memory=False)
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")

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
                log.info(f"Accelerometer or axis data found: {accel_candidates}")

            if not sensor_fields:
                raise ValueError("No valid IMU sensor data found in the file.")

            if time_candidates:
                timestamp_column = time_candidates[0]
                timestamps = df[timestamp_column].to_numpy()
                log.info(f"Timestamp column found: {timestamp_column}")

                combined_data = np.column_stack((timestamps.reshape(-1, 1), df[sensor_fields].to_numpy(dtype=np.float32)))
                columns = [timestamp_column] + sensor_fields
            else:
                timestamps = None
                combined_data = df[sensor_fields].to_numpy(dtype=np.float32)
                columns = sensor_fields
                log.info("No timestamp column found.")

            log.info(f"IMU file successfully read: {file_path} | Shape: {combined_data.shape} | Columns: {columns}")

            return {
                'data': combined_data,
                'timestamps': timestamps,
                'columns': columns
            }

        except Exception as e:
            raise ValueError(f"Failed to read IMU file {file_path}: {e}")

    def write(self, data_bundle: Dict[str, Any], file_path: str) -> None:
        file_ext = get_file_extension(file_path)
        if not validate_extension(file_path, self.supported_write_extensions):
            raise ValueError(f"Unsupported file extension for IMU: {file_ext}")

        if 'data' not in data_bundle or data_bundle['data'] is None:
            raise ValueError("Data bundle must contain 'data' key with valid IMU data.")

        data = data_bundle['data']
        columns = data_bundle.get('columns', [f'col_{i}' for i in range(data.shape[1])])

        if not isinstance(data, np.ndarray):
            raise ValueError("IMU data must be a NumPy array.")

        ensure_directory_exists(str(Path(file_path).parent))

        try:
            df = pd.DataFrame(data, columns=columns)
            df.to_csv(file_path, index=False)
        except Exception as e:
            raise ValueError(f"Failed to write IMU file {file_path}: {e}")

        log.info(f"IMU file successfully saved: {file_path} | Shape: {data.shape} | Columns: {columns}")


IORegistry.register_reader('imu', IMUIO)
IORegistry.register_writer('imu', IMUIO)