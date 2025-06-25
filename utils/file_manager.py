import shutil
import zipfile
from pathlib import Path
from typing import Optional, List
from logger.logger_manager import LoggerManager
from logger.logger_utils import shutdown_logger

# Initialise logger
log = LoggerManager.get_logger()


def human_readable_size(size_in_bytes: float, precision: int = 2) -> str:
    """
    Converts a size in bytes to a human-readable format (bytes, KB, MB, GB).

    Args:
        size_in_bytes (float): Size in bytes.
        precision (int): Number of decimal places.

    Returns:
        str: Formatted size string.
    """
    if size_in_bytes < 1024:
        return f"{size_in_bytes:.{precision}f} bytes"
    elif size_in_bytes < 1024 ** 2:
        return f"{size_in_bytes / 1024:.{precision}f} KB"
    elif size_in_bytes < 1024 ** 3:
        return f"{size_in_bytes / (1024 ** 2):.{precision}f} MB"
    else:
        return f"{size_in_bytes / (1024 ** 3):.{precision}f} GB"


def get_directory_size(directory: Path) -> float:
    """
    Calculates the total size of files in a directory (recursively).

    Returns:
        Size in bytes.
    """
    total_size = 0
    for file in directory.rglob('*'):
        if file.is_file():
            total_size += file.stat().st_size
    return total_size


def get_file_size(filepath: Path) -> float:
    """
    returns the file size.

    Returns:
        Size in bytes.
    """
    if filepath.is_file():
        return filepath.stat().st_size


def compress_file(file_path: Path, destination_dir: Path):
    """
    Compresses a file into a zip archive and deletes the original.

    Args:
        file_path (Path): The file to compress.
        destination_dir (Path): Directory to save the zip file.
    """
    destination_dir.mkdir(parents=True, exist_ok=True)
    zip_path = destination_dir / f"{file_path.stem}.zip"
    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.write(file_path, arcname=file_path.name)
    file_path.unlink()
    log.info(f"Compressed {file_path.name} -> {zip_path.name}")


def clean_directory(target_dir: Path, mode: str, retain_last_n: int,
                    file_extension: str, filter_keywords: Optional[List[str]],
                    compress: bool, requires_logger_shutdown: bool):
    """
    Cleans files in the target directory with flexible modes and optional compression.

    Args:
        target_dir (Path): Directory to clean.
        mode (str): 'full', 'files_only', 'retain_last_n'
        retain_last_n (int): Files to retain when using 'retain_last_n' mode.
        file_extension (str): File pattern to target (e.g., '*.log', '*.ckpt')
        filter_keywords (List[str]): List of required keywords to match in filenames.
        compress (bool): Compress files instead of deleting.
        requires_logger_shutdown (bool): Shuts down the logger handle file locks.
    """

    if not target_dir.exists():
        log.warning(f"Directory does not exist: {target_dir}")
        return

    def matches_filters(file_name: str) -> bool:
        if filter_keywords is None:
            return True
        return all(keyword in file_name for keyword in filter_keywords)

    initial_size = get_directory_size(target_dir)
    log.info(f"Initial directory size: {human_readable_size(initial_size)}")

    if mode == 'full':
        logger_active = True
        log.info(f"Deleting entire directory: {target_dir}")
        current_log_file = None

        if requires_logger_shutdown:
            log.info("Shutting down logger before directory cleanup...")
            shutdown_logger()
            shutil.rmtree(target_dir)
            logger_active = False
        else:
            logger_instance = LoggerManager.get_logger()
            for handler in logger_instance.handlers:
                if hasattr(handler, 'baseFilename'):
                    current_log_file = handler.baseFilename
                    break

            for file in target_dir.rglob('*'):
                if file.is_file():
                    if current_log_file and str(file.resolve()) == str(Path(current_log_file).resolve()):
                        log.info(f"Skipping currently active log file: {file}")
                        continue
                    file.unlink()
                    log.info(f"Deleted file: {file}")

            for sub_dir in sorted(target_dir.rglob('*'), key=lambda d: len(str(d)), reverse=True):
                if sub_dir.is_dir() and not any(sub_dir.iterdir()):
                    sub_dir.rmdir()
                    log.info(f"Removed empty directory: {sub_dir}")

        if not logger_active:
            LoggerManager.reinitialize_logger()
            log.info("Logger reinitialized after cleanup.")

    elif mode == 'files_only':
        log.info(f"Deleting files but keeping folder structure in: {target_dir}")
        current_log_file = None
        logger_active = True

        if requires_logger_shutdown:
            log.info("Shutting down logger before file cleanup...")
            shutdown_logger()
            logger_active = False
        else:
            # Get current active log file
            logger_instance = LoggerManager.get_logger()
            for handler in logger_instance.handlers:
                if hasattr(handler, 'baseFilename'):
                    current_log_file = handler.baseFilename
                    break

        for file in target_dir.rglob(file_extension):
            if matches_filters(file.name):
                if current_log_file and str(file.resolve()) == str(Path(current_log_file).resolve()):
                    log.info(f"Skipping currently active log file: {file}")
                    continue
                file.unlink()
                log.info(f"Deleted file: {file}")

        if not logger_active:
            LoggerManager.reinitialize_logger()
            log.info("Logger reinitialized after cleanup.")

    elif mode == 'retain_last_n':
        log.info(f"Retaining last {retain_last_n} files in: {target_dir}")
        for sub_dir in [target_dir] + [d for d in target_dir.iterdir() if d.is_dir()]:
            files = sorted(
                [f for f in sub_dir.glob(file_extension) if matches_filters(f.name)],
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            for old_file in files[retain_last_n:]:
                if compress:
                    compress_file(old_file, sub_dir / 'compressed')
                else:
                    old_file.unlink()
                    log.info(f"Deleted file: {old_file}")

    else:
        log.error("Invalid mode. Use 'full', 'files_only', or 'retain_last_n'.")
        raise ValueError("Invalid mode. Use 'full', 'files_only', or 'retain_last_n'.")

    final_size = get_directory_size(target_dir)
    log.info("Cleanup completed.")
    log.info(f"Final directory size: {human_readable_size(final_size)}")
    log.info(f"Disk space freed: {human_readable_size(initial_size - final_size)}")
