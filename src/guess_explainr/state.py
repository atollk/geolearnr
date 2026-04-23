import contextlib
import dataclasses
import json
import logging
import os.path
from collections.abc import Iterator
from dataclasses import dataclass

import platformdirs

_dirs = platformdirs.PlatformDirs("guess_explainr")
_config_file = os.path.join(_dirs.user_config_dir, "config.json")
logging.info(f"Loading config from {_config_file}")
os.makedirs(os.path.dirname(_config_file), exist_ok=True)


@dataclass
class InMemoryState:
    panorama_id: str | None = None


in_memory_state = InMemoryState()


@dataclass
class StateConfig:
    ai_provider: str | None = None
    ai_model: str | None = None


def get_config() -> StateConfig:
    try:
        with open(_config_file) as f:
            return StateConfig(**json.load(f))
    except FileNotFoundError:
        return StateConfig()


def set_config(config: StateConfig) -> None:
    with open(_config_file, "w") as f:
        json.dump(dataclasses.asdict(config), f)


@contextlib.contextmanager
def modify_config() -> Iterator[StateConfig]:
    config = get_config()
    yield config
    set_config(config)
