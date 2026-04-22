import json
import logging
import os.path
from typing import Any

import platformdirs
from frozendict import frozendict

_dirs = platformdirs.PlatformDirs("guess_explainr")
_config_file = os.path.join(_dirs.user_config_dir, "config.json")
logging.info(f"Loading config from {_config_file}")
os.makedirs(os.path.dirname(_config_file), exist_ok=True)


def get_config() -> frozendict[str, Any]:
    try:
        with open(_config_file) as f:
            return frozendict(json.load(f))
    except FileNotFoundError:
        return frozendict({})


def set_config(key: str, value: Any) -> None:
    set_config_values({key: value})


def set_config_values(d: dict[str, Any]) -> None:
    config = dict(get_config())
    config |= d
    with open(_config_file, "w") as f:
        json.dump(config, f)
