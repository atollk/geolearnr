_config: dict | None = None


def get_config() -> dict | None:
    return _config


def set_config(data: dict) -> None:
    global _config
    _config = data
