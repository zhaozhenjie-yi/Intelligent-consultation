"""Read credentials from environment variables or an ignored local JSON file."""
import json
import os
from pathlib import Path

_path = Path(__file__).with_name("local_settings.json")
_settings = json.loads(_path.read_text(encoding="utf-8-sig")) if _path.exists() else {}


def env(name):
    value = os.environ.get(name) or _settings.get(name)
    if not value:
        raise RuntimeError(f"Missing configuration: {name}. Set the environment variable or local_settings.json.")
    return value
