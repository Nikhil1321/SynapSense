# modality_io/lidar_io.py

from modality_io.base_io import BaseIO, IORegistry
from typing import Any, Optional
from pathlib import Path
import numpy as np
import open3d as o3d
import laspy
from configs.modality_config import SUPPORTED_EXTENSIONS
from logger.logger_manager import LoggerManager

# Initialise logger
log = LoggerManager.get_logger()


class LidarIO(BaseIO):
    def __init__(self):
        self.point_cloud: Optional[np.ndarray] = None
        self.supported_read_extensions = SUPPORTED_EXTENSIONS['lidar']['read']
        self.supported_write_extensions = SUPPORTED_EXTENSIONS['lidar']['write']

        IORegistry.register_reader('lidar', self.__class__)
        IORegistry.register_writer('lidar', self.__class__)

    def read(self, file_path: str) -> np.ndarray:
        if not self.validate_extension(Path(file_path).suffix, self.supported_read_extensions):
            raise ValueError(f"Unsupported file extension for LidarIO: {file_path}")

        ext = Path(file_path).suffix.lower()

        try:
            if ext in ['.pcd', '.ply']:
                pcd = o3d.io.read_point_cloud(str(file_path))
                self.point_cloud = np.asarray(pcd.points)

            elif ext in ['.las', '.laz']:
                las = laspy.read(file_path)
                self.point_cloud = np.vstack((las.x, las.y, las.z)).T

            elif ext == '.bin':
                self.point_cloud = np.fromfile(file_path, dtype=np.float32).reshape(-1, 4)

            else:
                raise ValueError(f"Unsupported file format: {ext}")

        except Exception as e:
            raise ValueError(f"Failed to read LiDAR file {file_path}: {e}")

        log.info(f"LiDAR file successfully read: {file_path} | Shape: {self.point_cloud.shape}")
        return self.point_cloud

    def write(self, data: Any = None, file_path: str = None) -> None:
        if file_path is None:
            raise ValueError("file_path must be provided for writing.")

        if data is None:
            if self.point_cloud is None:
                log.error("No point cloud loaded to write.")
                raise ValueError("No point cloud loaded to write.")
            data = self.point_cloud

        if not isinstance(data, np.ndarray) or data.shape[1] < 3:
            raise ValueError("LiDAR data must be a NumPy array with at least three columns (x, y, z).")

        if not self.validate_extension(Path(file_path).suffix, self.supported_write_extensions):
            raise ValueError(f"Unsupported file extension for LidarIO: {file_path}")

        ext = Path(file_path).suffix.lower()

        try:
            if ext in ['.pcd', '.ply']:
                pcd = o3d.geometry.PointCloud()
                pcd.points = o3d.utility.Vector3dVector(data[:, :3])
                o3d.io.write_point_cloud(str(file_path), pcd)

            elif ext in ['.las', '.laz']:
                header = laspy.LasHeader(point_format=3, version="1.2")
                las = laspy.LasData(header)
                las.x = data[:, 0]
                las.y = data[:, 1]
                las.z = data[:, 2]
                las.write(file_path)

            elif ext == '.bin':
                data.astype(np.float32).tofile(file_path)

            else:
                raise ValueError(f"Unsupported file format: {ext}")

        except Exception as e:
            raise ValueError(f"Failed to write LiDAR file {file_path}: {e}")

        log.info(f"LiDAR file successfully saved: {file_path} | Shape: {data.shape}")
