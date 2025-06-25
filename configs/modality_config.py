# modality_io/modality_config.py

# Supported file extensions for each modality

SUPPORTED_EXTENSIONS = {
    'dvs': {
        'read': ['.aedat4', '.txt', '.csv'],
        'write': ['.aedat4', '.csv']
    },
    'lidar': {
        'read': ['.pcd', '.ply', '.las', '.laz', '.bin'],
        'write': ['.pcd', '.ply', '.las', '.laz', '.bin']
    },
    'imu': {
        'read': ['.csv', '.txt'],
        'write': ['.csv']
    },
    'rgb': {
        'read': ['.png', '.jpg', 'jpeg', '.bmp'],
        'write': ['.png', '.jpg']
    }
}

LIDAR_PROCESSING_CONFIG = {
    'downsampling': {
        'method': 'voxel',  # Options: 'voxel', 'uniform', 'none'
        'voxel_size': 0.1,  # meters
        'uniform_every_k': 5
    },
    'outlier_removal': {
        'method': 'statistical',  # Options: 'statistical', 'radius', 'none'
        'statistical_nb_neighbors': 20,
        'statistical_std_ratio': 2.0,
        'radius_nb_points': 16,
        'radius_radius': 0.5  # meters
    },
    'resampling': {
        'method': 'random',  # Options: 'random', 'distance', 'none'
        'random_sample_size': 2048,
        'max_distance': 50.0  # meters
    }
}
