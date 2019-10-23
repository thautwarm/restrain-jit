from pathlib import Path
import json


class Configuration:
    # FIXME: better config obj
    config_dict: dict

    def __init__(self, config_dict):
        object.__setattr__(self, 'config_dict', config_dict)

    def __getattr__(self, item):
        val = self.config_dict[item]
        if isinstance(val, dict):
            return Configuration(val)
        return val

    def __setattr__(self, key, value):
        self.config_dict[key] = value

    def __delattr__(self, item):
        del self.config_dict[item]


RESTRAIN_DIR_PATH = Path("~/.restrain").expanduser()

RESTRAIN_CONFIG_FILE_PATH = RESTRAIN_DIR_PATH / "info.json"

if not RESTRAIN_DIR_PATH.exists(
) or not RESTRAIN_CONFIG_FILE_PATH.exists():
    # FIXME: auto create config
    raise RuntimeError("Python Restrain JIT not configured.")

with RESTRAIN_CONFIG_FILE_PATH.open() as f:
    RESTRAIN_CONFIG = Configuration(json.load(f))
del f
