"""Configuration helpers for PyMacroRecorder."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from appdirs import user_data_dir

APP_NAME = "PyMacroRecorder"
APP_AUTHOR = "PyMacroRecorder"
CONFIG_NAME = "config.json"

DEFAULT_HOTKEYS: Dict[str, List[str]] = {
    "start_record": ["<ctrl>", "<alt>", "r"],
    "stop_record": ["<ctrl>", "<alt>", "s"],
    "start_macro": ["<ctrl>", "<alt>", "p"],
    "stop_macro": ["<ctrl>", "<alt>", "o"],
    "save_macro": ["<ctrl>", "<alt>", "e"],
    "load_macro": ["<ctrl>", "<alt>", "l"],
}


def _config_path() -> Path:
    data_dir = Path(user_data_dir(APP_NAME, APP_AUTHOR))
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / CONFIG_NAME


def load_config() -> Dict[str, Dict[str, List[str]]]:
    path = _config_path()
    if not path.exists():
        return {"hotkeys": DEFAULT_HOTKEYS.copy()}
    try:
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
    except Exception:
        return {"hotkeys": DEFAULT_HOTKEYS.copy()}
    hotkeys = data.get("hotkeys", {})
    merged = DEFAULT_HOTKEYS.copy()
    merged.update({k: v for k, v in hotkeys.items() if isinstance(v, list)})
    return {"hotkeys": merged}


def save_config(config: Dict[str, Dict[str, List[str]]]) -> None:
    path = _config_path()
    payload = {"hotkeys": config.get("hotkeys", DEFAULT_HOTKEYS)}
    with path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)


