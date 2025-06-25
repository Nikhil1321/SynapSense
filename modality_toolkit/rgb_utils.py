# modality_toolkit/rgb_utils.py

import cv2
import numpy as np
from typing import Tuple


def resize_image(image: np.ndarray, size: Tuple[int, int]) -> np.ndarray:
    if image is None or not isinstance(image, np.ndarray):
        raise ValueError("Input image must be a valid NumPy array.")
    if not (isinstance(size, tuple) and len(size) == 2):
        raise ValueError("Size must be a tuple of (width, height).")
    if size[0] <= 0 or size[1] <= 0:
        raise ValueError("Resize dimensions must be positive integers.")

    return cv2.resize(image, size, interpolation=cv2.INTER_LINEAR)


def crop_image(image: np.ndarray, box: Tuple[int, int, int, int]) -> np.ndarray:
    if image is None or not isinstance(image, np.ndarray):
        raise ValueError("Input image must be a valid NumPy array.")
    if not (isinstance(box, tuple) and len(box) == 4):
        raise ValueError("Box must be a tuple of (x_min, y_min, x_max, y_max).")

    x_min, y_min, x_max, y_max = box
    h, w = image.shape[:2]

    if not (0 <= x_min < x_max <= w and 0 <= y_min < y_max <= h):
        raise ValueError(f"Crop box {box} is out of image bounds {w}x{h}.")

    return image[y_min:y_max, x_min:x_max]


def rotate_image(image: np.ndarray, angle: float) -> np.ndarray:
    if image is None or not isinstance(image, np.ndarray):
        raise ValueError("Input image must be a valid NumPy array.")
    if not isinstance(angle, (int, float)):
        raise ValueError("Angle must be a numeric value.")

    h, w = image.shape[:2]
    center = (w // 2, h // 2)
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, scale=1.0)

    return cv2.warpAffine(image, rotation_matrix, (w, h))


def flip_image_horizontal(image: np.ndarray) -> np.ndarray:
    if image is None or not isinstance(image, np.ndarray):
        raise ValueError("Input image must be a valid NumPy array.")

    return cv2.flip(image, 1)


def flip_image_vertical(image: np.ndarray) -> np.ndarray:
    if image is None or not isinstance(image, np.ndarray):
        raise ValueError("Input image must be a valid NumPy array.")

    return cv2.flip(image, 0)
