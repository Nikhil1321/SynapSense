# modality_io/dvs.py

from modality_io.base_io import BaseIO, IORegistry
from modality_io.utils import validate_extension, get_file_extension, ensure_directory_exists
from typing import Any, Dict
from pathlib import Path
import numpy as np
import pandas as pd
from configs.modality_config import SUPPORTED_EXTENSIONS
from logger.logger_manager import LoggerManager

# Try importing .aedat4 libraries
try:
    import aedat
except ImportError:
    aedat = None

try:
    import dv_processing as dv
except ImportError:
    dv = None

log = LoggerManager.get_logger()


class DVSIO(BaseIO):
    def __init__(self):
        self.supported_read_extensions = SUPPORTED_EXTENSIONS['dvs']['read']
        self.supported_write_extensions = SUPPORTED_EXTENSIONS['dvs']['write']

        # IORegistry.register_reader('dvs', self.__class__)
        # IORegistry.register_writer('dvs', self.__class__)

    def read(self, file_path: str) -> Dict[str, Any]:
        file_ext = get_file_extension(file_path)
        if not validate_extension(file_path, self.supported_read_extensions):
            raise ValueError(f"Unsupported DVS file type: {file_ext}")

        try:
            if file_ext in ['.csv', '.txt']:
                df = (pd.read_csv(file_path)
                      if file_ext == '.csv'
                      else pd.read_csv(file_path, delimiter=r'\s+'))
                required = {'t', 'x', 'y', 'p'}
                if not required.issubset(df.columns.str.lower()):
                    raise ValueError("Missing DVS columns: t, x, y, p")

                events = df[['t', 'x', 'y', 'p']].to_numpy(dtype=np.float32)
                timestamps = df['t'].to_numpy()
                columns = ['t', 'x', 'y', 'p']

            elif file_ext == '.aedat4':
                if aedat is None:
                    raise ImportError("`aedat` library is required for .aedat4 reading.")
                decoder = aedat.Decoder(file_path)
                events_list = []
                for packet in decoder:
                    if "events" in packet:
                        ev = packet["events"]
                        t = ev['t'].astype(np.float64)
                        x = ev['x'].astype(np.float32)
                        y = ev['y'].astype(np.float32)
                        p = ev['on'].astype(np.int8)
                        events_list.append(np.column_stack((t, x, y, p)))

                if not events_list:
                    raise ValueError("No events found in .aedat4 file.")
                events = np.vstack(events_list)
                timestamps = events[:, 0]
                columns = ['t', 'x', 'y', 'p']

            else:
                raise ValueError(f"Unsupported DVS file extension: {file_ext}")

            log.info(f"DVS data read: {events.shape} from {file_path}")
            return {'data': events, 'timestamps': timestamps, 'columns': columns}

        except Exception as e:
            raise ValueError(f"Failed reading DVS file {file_path}: {e}")

    def write(self, data_bundle: Dict[str, Any], file_path: str) -> None:
        file_ext = get_file_extension(file_path)
        if not validate_extension(file_path, self.supported_write_extensions):
            raise ValueError(f"Unsupported DVS file type: {file_ext}")

        data = data_bundle.get('data')
        if data is None or not isinstance(data, np.ndarray) or data.shape[1] != 4:
            raise ValueError("DVS 'data' must be a NumPy array of shape (N, 4).")

        columns = data_bundle.get('columns', ['t', 'x', 'y', 'p'])
        ensure_directory_exists(str(Path(file_path).parent))

        try:
            if file_ext in ['.csv', '.txt']:
                df = pd.DataFrame(data, columns=columns)
                if file_ext == '.csv':
                    df.to_csv(file_path, index=False)
                else:
                    df.to_csv(file_path, sep='\t', index=False)

            elif file_ext == '.aedat4':
                if dv is None:
                    raise ImportError("`dv-processing` is required for .aedat4 writing.")
                # Use DVS-only config to create an AEDAT4 writer
                config = dv.io.MonoCameraWriter.DVSConfig("DVS_Output", (0, 0))
                writer = dv.io.MonoCameraWriter(str(file_path), config)
                # 'events' is a dv.EventStore structured type
                store = dv.data.EventStore()
                timestamps, xs, ys, ps = data.T
                store.push_back(timestamps, xs, ys, ps.astype(bool))
                writer.writeEvents(store)
                writer.close()

            else:
                raise ValueError(f"Unsupported DVS output extension: {file_ext}")

        except Exception as e:
            raise ValueError(f"Failed writing DVS file {file_path}: {e}")

        log.info(f"DVS data saved: {data.shape} to {file_path}")

IORegistry.register_reader('dvs', DVSIO)
IORegistry.register_writer('dvs', DVSIO)