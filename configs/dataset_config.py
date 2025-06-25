# dataset_configs.py
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

AVAILABLE_DATASET = {
    'DSEC': {
        'description': 'A Stereo Event Camera Dataset for Driving Scenarios',
        'available_modality': '2x monochrome event cameras, 2x global shutter color cameras, 1x LiDAR data, '
                              'and 1x RTK GPS measurements'
    },
    'KITTI': {
        'description': 'A comprehensive dataset from Karlsruhe Institute of Technology (KIT) for novel challenging'
                       ' real-world computer vision benchmarks',
        'available_modality': '1x Inertial Navigation System (GPS/IMU), 1x Laser scanner, 2x Grayscale cameras, '
                              '2x Color cameras and 4x Varifocal lenses'
    },
    'nuScenes': {
        'description': 'nuScenes is a public large-scale dataset for autonomous driving using the full sensor '
                       'suite of a real self-driving car.',
        'available_modality': '1x LiDAR, 5x RADAR, 6x camera, 1x IMU and 1x GPS'
    },
    'MVSEC': {
        'description': 'The Multi Vehicle Stereo Event Camera dataset for 3D perception algorithms for '
                       'event-based cameras.',
        'available_modality': '2x Event Camera (DAVIS), 1x LiDAR, 1x GPS, 1x VI Sensor and 2x Motion Capture'
    },
    'IODataset': {
        'description': 'Sample dataset to check IO capability. With single image from each format.',
        'available_modality': 'Image, LiDAR, IMU, DVS'
    }
}

# Dataset-specific sub-folders
DATASET_DIRS = {
    'DSEC': {'root': 'DSEC'},
    'KITTI': {'root': 'KITTI'},
    'nuScenes': {'root': 'nuScenes'},
    'MVSEC': {'root': 'MVSEC'},
    'IODataset': {
        'root': 'IODataset',
        'image': 'image',
        'lidar': 'lidar',
        'imu': 'imu',
        'event': 'dvs'
    }
}