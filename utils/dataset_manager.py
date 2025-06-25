# dataset_manager.py

import urllib.request
from configs.dataset_config import AVAILABLE_DATASET
from utils.path_manager import get_dataset_path
from logger.logger_manager import LoggerManager

# Initialise logger
log = LoggerManager.get_logger()


def show_available_datasets():
    log.info("Available Datasets:\n")
    for dataset, detail in AVAILABLE_DATASET.items():
        log.info(f"{dataset}:\n  Description: {detail['description']}\n  Modalities: {detail['available_modality']}\n")


def validate_dataset(dataset_name, modality=None):
    dataset_path = get_dataset_path(dataset_name, modality)
    if not dataset_path.exists():
        log.info(f"[ERROR] Dataset path does not exist: {dataset_path}")
        return False
    log.info(f"[OK] Dataset path exists: {dataset_path}")
    return True


def list_dataset_files(dataset_name, modality=None):
    from collections import defaultdict
    from pathlib import Path

    dataset_path = get_dataset_path(dataset_name, modality)

    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset path does not exist: {dataset_path}")

    log.info(f"\nListing files in: {dataset_path}\n")

    def list_directory(path: Path, indent: int = 0):
        entries = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
        files_by_extension = defaultdict(list)
        found_any_files = False

        for entry in entries:
            if entry.is_dir():
                log.info('    ' * indent + f"{entry.name}/")
                sub_found_files = list_directory(entry, indent + 1)
                if not sub_found_files:
                    log.info('    ' * (indent + 1) + "(No files available)")
                else:
                    found_any_files = True
            elif entry.is_file():
                files_by_extension[entry.suffix.lower()].append(entry.name)
                found_any_files = True

        for ext, files in files_by_extension.items():
            file_list_preview = ', '.join(files[:3]) + (', ...' if len(files) > 3 else '')
            ext_display = ext if ext else '[No Extension]'
            log.info('    ' * indent + f"{len(files)} *{ext_display} - {file_list_preview}")

        return found_any_files

    has_any_files = list_directory(dataset_path)

    if not has_any_files:
        log.info("(No files found in this dataset)")

    return dataset_path


def download_dataset(dataset_name, url, overwrite=False):
    dataset_path = get_dataset_path(dataset_name)
    dataset_zip = dataset_path.with_suffix('.zip')

    if dataset_path.exists() and not overwrite:
        log.info(f"[INFO] Dataset already exists at {dataset_path}. Skipping download.")
        return

    dataset_path.mkdir(parents=True, exist_ok=True)

    log.info(f"Downloading {dataset_name} from {url} ...")
    try:
        urllib.request.urlretrieve(url, dataset_zip)
        log.info(f"Downloaded to {dataset_zip}")
        # You can optionally add zip extraction here
    except Exception as e:
        log.info(f"[ERROR] Failed to download dataset: {e}")
