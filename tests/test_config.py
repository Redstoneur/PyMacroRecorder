"""Tests de configuration (load/save)."""

import json
from pathlib import Path

from pymacrorecorder import config



def test_load_config_defaults_when_missing(monkeypatch, tmp_path: Path) -> None:
    """Retourne les valeurs par defaut si le fichier manque."""
    cfg_path = tmp_path / "config.json"
    monkeypatch.setattr(config, "_config_path", lambda: cfg_path)

    data = config.load_config()

    assert data["hotkeys"] == config.DEFAULT_HOTKEYS



def test_load_config_invalid_json(monkeypatch, tmp_path: Path) -> None:
    """Retourne les valeurs par defaut si le JSON est invalide."""
    cfg_path = tmp_path / "config.json"
    cfg_path.write_text("{broken", encoding="utf-8")
    monkeypatch.setattr(config, "_config_path", lambda: cfg_path)

    data = config.load_config()

    assert data["hotkeys"] == config.DEFAULT_HOTKEYS



def test_load_config_sanitizes_hotkeys(monkeypatch, tmp_path: Path) -> None:
    """Normalise et valide les hotkeys lues du fichier."""
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
    """Normalise avant ecriture sur disque."""
    cfg_path = tmp_path / "config.json"
    monkeypatch.setattr(config, "_config_path", lambda: cfg_path)

    config.save_config({"hotkeys": {"start_record": ["<CTRL>", "R"]}})

    saved = json.loads(cfg_path.read_text(encoding="utf-8"))
    assert saved["hotkeys"]["start_record"] == ["<ctrl>", "r"]
