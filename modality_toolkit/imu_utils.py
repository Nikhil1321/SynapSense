import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt
from logger.logger_manager import LoggerManager

log = LoggerManager.get_logger()


def extract_sensor_data(imu_data: np.ndarray, with_time: bool = True) -> np.ndarray:
    if imu_data.shape[1] < 3:
        raise ValueError("IMU data must have at least 3 columns (gyro/accel data).")

    if with_time:
        return imu_data[:, 1:]
    else:
        return imu_data


def moving_average_filter(imu_data: np.ndarray, window_size: int = 5, with_time: bool = True) -> np.ndarray:
    data = extract_sensor_data(imu_data, with_time)
    filtered = np.convolve(data[:, 0], np.ones(window_size) / window_size, mode='same')[:, None]
    for i in range(1, data.shape[1]):
        filtered = np.hstack((filtered, np.convolve(data[:, i], np.ones(window_size) / window_size, mode='same')[:, None]))

    if with_time:
        result = np.hstack((imu_data[:, 0].reshape(-1, 1), filtered))
    else:
        result = filtered

    log.info(f"Moving average filter applied | Window size: {window_size}")
    return result


def low_pass_filter(imu_data: np.ndarray, cutoff_freq: float, sampling_rate: float, order: int = 3, with_time: bool = True) -> np.ndarray:
    data = extract_sensor_data(imu_data, with_time)
    nyquist = 0.5 * sampling_rate
    normal_cutoff = cutoff_freq / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    filtered = filtfilt(b, a, data, axis=0)

    if with_time:
        result = np.hstack((imu_data[:, 0].reshape(-1, 1), filtered))
    else:
        result = filtered

    log.info(f"Low-pass filter applied | Cutoff: {cutoff_freq}Hz | Sampling rate: {sampling_rate}Hz | Order: {order}")
    return result


def resample_imu(imu_data: np.ndarray, target_frequency: float, with_time: bool = True) -> np.ndarray:
    if imu_data.shape[1] < 2:
        raise ValueError("IMU data must have at least 2 columns (time + sensor data) for resampling.")

    if with_time:
        timestamps = imu_data[:, 0]
        data = imu_data[:, 1:]
    else:
        raise ValueError("Resampling requires timestamp information.")

    df = pd.DataFrame(data, index=pd.to_datetime(timestamps, unit='s'))
    resample_interval = f"{int(1e3 / target_frequency)}L"

    resampled_df = df.resample(resample_interval).mean().interpolate()

    resampled_time = (resampled_df.index.astype(np.int64) / 1e9).reshape(-1, 1)
    resampled_data = resampled_df.to_numpy()

    result = np.hstack((resampled_time, resampled_data))
    log.info(f"Resampling applied | Target frequency: {target_frequency}Hz | Result shape: {result.shape}")
    return result


def normalize_imu(imu_data: np.ndarray, with_time: bool = True) -> np.ndarray:
    data = extract_sensor_data(imu_data, with_time)
    mean = np.mean(data, axis=0)
    std = np.std(data, axis=0)
    normalized = (data - mean) / (std + 1e-8)

    if with_time:
        result = np.hstack((imu_data[:, 0].reshape(-1, 1), normalized))
    else:
        result = normalized

    log.info("Normalization applied | Zero-mean unit-variance per axis")
    return result
