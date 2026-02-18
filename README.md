# PyMacroRecorder

---

![License](https://img.shields.io/github/license/Redstoneur/PyMacroRecorder)
![Top Language](https://img.shields.io/github/languages/top/Redstoneur/PyMacroRecorder)
![Python Version](https://img.shields.io/badge/python-3.14.0-blue)
![Size](https://img.shields.io/github/repo-size/Redstoneur/PyMacroRecorder)
![Contributors](https://img.shields.io/github/contributors/Redstoneur/PyMacroRecorder)
![Last Commit](https://img.shields.io/github/last-commit/Redstoneur/PyMacroRecorder)
![Issues](https://img.shields.io/github/issues/Redstoneur/PyMacroRecorder)
![Pull Requests](https://img.shields.io/github/issues-pr/Redstoneur/PyMacroRecorder)

---

![Forks](https://img.shields.io/github/forks/Redstoneur/PyMacroRecorder)
![Stars](https://img.shields.io/github/stars/Redstoneur/PyMacroRecorder)
![Watchers](https://img.shields.io/github/watchers/Redstoneur/PyMacroRecorder)

---

![Latest Release](https://img.shields.io/github/v/release/Redstoneur/PyMacroRecorder)
![Release Date](https://img.shields.io/github/release-date/Redstoneur/PyMacroRecorder)
[![Build Status](https://github.com/Redstoneur/PyMacroRecorder/actions/workflows/ci.yml/badge.svg)](https://github.com/Redstoneur/PyMacroRecorder/actions/workflows/ci.yml)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/1626228dee914e71b2805544b1b5094d)](https://app.codacy.com/gh/Redstoneur/PyMacroRecorder/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)

---

Tkinter app to record, play, and save keyboard/mouse macros.

## Features

- Global recording (pynput) with live log.
- Buttons: Start/Stop Record, Start/Stop Macro, Save Macro, Load Macro.
- Configurable global hotkeys (minimum 2 keys). Control combos are ignored during recording.
- Save/load macros as CSV (name + events JSON). The displayed preview is what is replayed.
- Playback with repeat count (0 = infinite) and immediate stop.

## Structure

```
PyMacroRecorder/
├─ main.py
├─ requirements.txt
├─ pyproject.toml
├─ README.md
├─ LICENSE
├─ CONTRIBUTING.md
├─ build.ps1
├─ build.sh
├─ .gitignore
├─ .github/
│  └─ workflows/
│     ├─ ci.yml 
│     └─ release.yml
└─ pymacrorecorder/
   ├─ __init__.py
   ├─ app.py
   ├─ config.py
   ├─ hotkeys.py
   ├─ models.py
   ├─ player.py
   ├─ recorder.py
   ├─ storage.py
   └─ utils.py
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: `.venv\Scripts\activate`
pip install -r requirements.txt
python main.py
```

## Save & config

- Macros: CSV chosen via the UI (columns `name`, `events`).
- Hotkeys: `config.json` in the user data directory (see `pymacrorecorder/config.py`).

## Default hotkeys

- Start Record: Ctrl+Alt+R
- Stop Record: Ctrl+Alt+S
- Start Macro: Ctrl+Alt+P
- Stop Macro: Ctrl+Alt+O
- Save Macro: Ctrl+Alt+E
- Load Macro: Ctrl+Alt+L

Click a hotkey label in the UI, press a new combination (≥2 keys) to save it.
