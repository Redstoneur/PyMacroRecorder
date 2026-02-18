"""Configuration tests (load/save).

This module tests the configuration loading and saving functionality,
including default value handling, JSON validation, hotkey normalization,
and configuration persistence.
"""

import json
from pathlib import Path

from pymacrorecorder import config



def test_load_config_defaults_when_missing(monkeypatch, tmp_path: Path) -> None:
    """Returns default values if the config file is missing.

    Verifies that load_config returns DEFAULT_HOTKEYS when the
    configuration file does not exist.

    :param monkeypatch: Pytest monkeypatch fixture
    :param tmp_path: Pytest temporary directory fixture
    :type tmp_path: Path
    :return: None
    :rtype: None
    """
    cfg_path = tmp_path / "config.json"
    monkeypatch.setattr(config, "_config_path", lambda: cfg_path)

    data = config.load_config()

    assert data["hotkeys"] == config.DEFAULT_HOTKEYS



def test_load_config_invalid_json(monkeypatch, tmp_path: Path) -> None:
    """Returns default values if the JSON is invalid.

    Verifies that load_config handles malformed JSON gracefully by
    returning default configuration values.

    :param monkeypatch: Pytest monkeypatch fixture
    :param tmp_path: Pytest temporary directory fixture
    :type tmp_path: Path
    :return: None
    :rtype: None
    """
    cfg_path = tmp_path / "config.json"
    cfg_path.write_text("{broken", encoding="utf-8")
    monkeypatch.setattr(config, "_config_path", lambda: cfg_path)

    data = config.load_config()

    assert data["hotkeys"] == config.DEFAULT_HOTKEYS



def test_load_config_sanitizes_hotkeys(monkeypatch, tmp_path: Path) -> None:
    """Normalizes and validates hotkeys read from the file.

    Verifies that load_config normalizes hotkey case, validates format,
    and replaces invalid hotkeys with defaults.

    :param monkeypatch: Pytest monkeypatch fixture
    :param tmp_path: Pytest temporary directory fixture
    :type tmp_path: Path
    :return: None
    :rtype: None
    """
    cfg_path = tmp_path / "config.json"
    payload = {
        "hotkeys": {
            "start_record": ["<CTRL>", "R"],
            "stop_record": ["bad"],
            "save_macro": "not-a-list",
        }
    }
    cfg_path.write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.setattr(config, "_config_path", lambda: cfg_path)

    data = config.load_config()

    assert data["hotkeys"]["start_record"] == ["<ctrl>", "r"]
    assert data["hotkeys"]["stop_record"] == config.DEFAULT_HOTKEYS["stop_record"]
    assert data["hotkeys"]["save_macro"] == config.DEFAULT_HOTKEYS["save_macro"]



def test_save_config_normalizes(monkeypatch, tmp_path: Path) -> None:
    """Normalizes hotkeys before writing to disk.

    Verifies that save_config normalizes hotkey case before persisting
    the configuration to the JSON file.

    :param monkeypatch: Pytest monkeypatch fixture
    :param tmp_path: Pytest temporary directory fixture
    :type tmp_path: Path
    :return: None
    :rtype: None
    """
    cfg_path = tmp_path / "config.json"
    monkeypatch.setattr(config, "_config_path", lambda: cfg_path)

    config.save_config({"hotkeys": {"start_record": ["<CTRL>", "R"]}})

    saved = json.loads(cfg_path.read_text(encoding="utf-8"))
    assert saved["hotkeys"]["start_record"] == ["<ctrl>", "r"]
