# modality_io/lidar.py

from modality_io.base_io import BaseIO, IORegistry
from modality_io.utils import validate_extension, get_file_extension, ensure_directory_exists
from typing import Any, Dict
from pathlib import Path
import numpy as np
import open3d as o3d
import laspy
from configs.modality_config import SUPPORTED_EXTENSIONS
from logger.logger_manager import LoggerManager

# Initialize logger
log = LoggerManager.get_logger()


class LidarIO(BaseIO):
    def __init__(self):
        self.supported_read_extensions = SUPPORTED_EXTENSIONS['lidar']['read']
        self.supported_write_extensions = SUPPORTED_EXTENSIONS['lidar']['write']

        # IORegistry.register_reader('lidar', self.__class__)
        # IORegistry.register_writer('lidar', self.__class__)

    def read(self, file_path: str) -> Dict[str, Any]:
        file_ext = get_file_extension(file_path)
        if not validate_extension(file_path, self.supported_read_extensions):
            raise ValueError(f"Unsupported file extension for LiDAR: {file_ext}")

        try:
            if file_ext in ['.pcd', '.ply']:
                pcd = o3d.io.read_point_cloud(str(file_path))
                point_cloud = np.asarray(pcd.points)

            elif file_ext in ['.las', '.laz']:
                las = laspy.read(file_path)
                point_cloud = np.vstack((las.x, las.y, las.z)).T

            elif file_ext == '.bin':
                point_cloud = np.fromfile(file_path, dtype=np.float32).reshape(-1, 4)

            else:
                raise ValueError(f"Unsupported file format: {file_ext}")

            log.info(f"LiDAR file successfully read: {file_path} | Shape: {point_cloud.shape}")

            return {
                'data': point_cloud,
                'timestamps': None,  # LiDAR files typically don't carry per-point timestamps
                'columns': ['X', 'Y', 'Z']  # Generic column labels for point clouds
            }

        except Exception as e:
            raise ValueError(f"Failed to read LiDAR file {file_path}: {e}")

    def write(self, data_bundle: Dict[str, Any], file_path: str) -> None:
        file_ext = get_file_extension(file_path)
        if not validate_extension(file_path, self.supported_write_extensions):
            raise ValueError(f"Unsupported file extension for LiDAR: {file_ext}")

        if 'data' not in data_bundle or data_bundle['data'] is None:
            raise ValueError("Data bundle must contain 'data' key with valid LiDAR point cloud data.")

        data = data_bundle['data']

        if not isinstance(data, np.ndarray) or data.shape[1] < 3:
            raise ValueError("LiDAR data must be a NumPy array with at least three columns (X, Y, Z).")

        ensure_directory_exists(str(Path(file_path).parent))

        try:
            if file_ext in ['.pcd', '.ply']:
                pcd = o3d.geometry.PointCloud()
                pcd.points = o3d.utility.Vector3dVector(data[:, :3])
                o3d.io.write_point_cloud(str(file_path), pcd)

            elif file_ext in ['.las', '.laz']:
                header = laspy.LasHeader(point_format=3, version="1.2")
                las = laspy.LasData(header)
                las.x = data[:, 0]
                las.y = data[:, 1]
                las.z = data[:, 2]
                las.write(file_path)

            elif file_ext == '.bin':
                data.astype(np.float32).tofile(file_path)

            else:
                raise ValueError(f"Unsupported file format: {file_ext}")

        except Exception as e:
            raise ValueError(f"Failed to write LiDAR file {file_path}: {e}")

        log.info(f"LiDAR file successfully saved: {file_path} | Shape: {data.shape}")


IORegistry.register_reader('lidar', LidarIO)
IORegistry.register_writer('lidar', LidarIO)