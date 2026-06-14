import json
import os
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "config.json"

DEFAULT_CONFIG = {
    "devtrack_path": "",
    "gitpush_path": "",
    "user_name": "",
    "github_username": "",
    "setup_complete": False,
    "daily_goal_hours": 8,
    "roadmap_start_date": "",
    "current_week": 1,
    "current_month": 1,
}


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        return DEFAULT_CONFIG.copy()
    try:
        with open(CONFIG_PATH, "r") as f:
            data = json.load(f)
        return {**DEFAULT_CONFIG, **data}
    except (json.JSONDecodeError, IOError):
        return DEFAULT_CONFIG.copy()


def save_config(config: dict) -> None:
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)


def update_config(**kwargs) -> None:
    config = load_config()
    config.update(kwargs)
    save_config(config)


def get(key: str):
    return load_config().get(key, DEFAULT_CONFIG.get(key))


def is_setup_complete() -> bool:
    return load_config().get("setup_complete", False)


def get_devtrack_data() -> dict:
    """Read devtrack_data.json from the configured DevTrack path."""
    devtrack_path = get("devtrack_path")
    if not devtrack_path:
        return {}

    data_file = Path(devtrack_path) / "devtrack_data.json"
    if not data_file.exists():
        return {}

    try:
        with open(data_file, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def validate_devtrack_path(path: str) -> bool:
    """Check if a path contains a valid DevTrack installation."""
    p = Path(path)
    return p.exists() and p.is_dir()


def validate_gitpush_path(path: str) -> bool:
    """Check if a path contains a valid GitPush installation."""
    p = Path(path)
    return (p / "git_ops.py").exists()
