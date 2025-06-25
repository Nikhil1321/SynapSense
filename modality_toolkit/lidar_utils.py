# modality_toolkit/lidar_utils.py

import numpy as np
import open3d as o3d
from logger.logger_manager import LoggerManager
from configs.modality_config import LIDAR_PROCESSING_CONFIG

log = LoggerManager.get_logger()


def to_open3d_point_cloud(point_cloud: np.ndarray) -> o3d.geometry.PointCloud:
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(point_cloud[:, :3])
    return pcd


def from_open3d_point_cloud(pcd: o3d.geometry.PointCloud, original_dim: int) -> np.ndarray:
    processed_points = np.asarray(pcd.points)
    if original_dim == 4:
        processed_points = np.hstack((processed_points, np.zeros((processed_points.shape[0], 1))))
    return processed_points


# Downsampling Methods

def voxel_downsample(point_cloud: np.ndarray, voxel_size: float = None) -> np.ndarray:
    voxel_size = voxel_size or LIDAR_PROCESSING_CONFIG['downsampling']['voxel_size']
    pcd = to_open3d_point_cloud(point_cloud)
    downsampled_pcd = pcd.voxel_down_sample(voxel_size=voxel_size)
    log.info(f"Voxel downsampling applied | Voxel size: {voxel_size} | Reduced to {len(downsampled_pcd.points)} points")
    return from_open3d_point_cloud(downsampled_pcd, point_cloud.shape[1])


def uniform_downsample(point_cloud: np.ndarray, every_k_points: int = None) -> np.ndarray:
    every_k_points = every_k_points or LIDAR_PROCESSING_CONFIG['downsampling']['uniform_every_k']
    pcd = to_open3d_point_cloud(point_cloud)
    downsampled_pcd = pcd.uniform_down_sample(every_k_points=every_k_points)
    log.info(f"Uniform downsampling applied | Every {every_k_points}th point retained | Remaining points: {len(downsampled_pcd.points)}")
    return from_open3d_point_cloud(downsampled_pcd, point_cloud.shape[1])


# Outlier and Noise Removal

def statistical_outlier_removal(point_cloud: np.ndarray, nb_neighbors: int = None, std_ratio: float = None) -> np.ndarray:
    nb_neighbors = nb_neighbors or LIDAR_PROCESSING_CONFIG['outlier_removal']['statistical_nb_neighbors']
    std_ratio = std_ratio or LIDAR_PROCESSING_CONFIG['outlier_removal']['statistical_std_ratio']
    pcd = to_open3d_point_cloud(point_cloud)
    cl, ind = pcd.remove_statistical_outlier(nb_neighbors=nb_neighbors, std_ratio=std_ratio)
    filtered_pcd = pcd.select_by_index(ind)
    log.info(f"Statistical outlier removal applied | Remaining points: {len(filtered_pcd.points)}")
    return from_open3d_point_cloud(filtered_pcd, point_cloud.shape[1])


def radius_outlier_removal(point_cloud: np.ndarray, nb_points: int = None, radius: float = None) -> np.ndarray:
    nb_points = nb_points or LIDAR_PROCESSING_CONFIG['outlier_removal']['radius_nb_points']
    radius = radius or LIDAR_PROCESSING_CONFIG['outlier_removal']['radius_radius']
    pcd = to_open3d_point_cloud(point_cloud)
    cl, ind = pcd.remove_radius_outlier(nb_points=nb_points, radius=radius)
    filtered_pcd = pcd.select_by_index(ind)
    log.info(f"Radius outlier removal applied | Remaining points: {len(filtered_pcd.points)}")
    return from_open3d_point_cloud(filtered_pcd, point_cloud.shape[1])


# Resampling

def random_sampling(point_cloud: np.ndarray, num_samples: int = None) -> np.ndarray:
    num_samples = num_samples or LIDAR_PROCESSING_CONFIG['resampling']['random_sample_size']
    if point_cloud.shape[0] <= num_samples:
        log.info("Random sampling skipped: dataset already smaller than requested sample size.")
        return point_cloud

    indices = np.random.choice(point_cloud.shape[0], num_samples, replace=False)
    sampled = point_cloud[indices]
    log.info(f"Random sampling applied | Sample size: {num_samples}")
    return sampled


def distance_clipping(point_cloud: np.ndarray, max_distance: float = None) -> np.ndarray:
    max_distance = max_distance or LIDAR_PROCESSING_CONFIG['resampling']['max_distance']
    distances = np.linalg.norm(point_cloud[:, :3], axis=1)
    clipped = point_cloud[distances <= max_distance]
    log.info(f"Distance clipping applied | Max distance: {max_distance} | Remaining points: {len(clipped)}")
    return clipped


# Voxel Grid Creation

def create_voxel_grid(point_cloud: np.ndarray, voxel_size: float = None) -> o3d.geometry.VoxelGrid:
    voxel_size = voxel_size or LIDAR_PROCESSING_CONFIG['downsampling']['voxel_size']
    pcd = to_open3d_point_cloud(point_cloud)
    voxel_grid = o3d.geometry.VoxelGrid.create_from_point_cloud(pcd, voxel_size=voxel_size)
    log.info(f"Voxel grid created | Voxel size: {voxel_size} | Number of voxels: {len(voxel_grid.get_voxels())}")
    return voxel_grid
