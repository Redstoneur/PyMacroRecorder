# PyMacroRecorder

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
