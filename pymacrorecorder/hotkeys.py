"""Global hotkey management."""

from __future__ import annotations

import threading
from typing import Callable, Dict, List, Optional

from pynput import keyboard

from .utils import format_combo

HotkeyCallback = Callable[[str], None]


class HotkeyManager:
    def __init__(self, mapping: Dict[str, List[str]], dispatcher: HotkeyCallback):
        self.mapping = mapping
        self.dispatcher = dispatcher
        self._listener: Optional[keyboard.GlobalHotKeys] = None
        self._lock = threading.Lock()

    def start(self) -> None:
        with self._lock:
            self._restart()

    def stop(self) -> None:
        with self._lock:
            if self._listener:
                self._listener.stop()
                self._listener = None

    def update(self, mapping: Dict[str, List[str]]) -> None:
        with self._lock:
            self.mapping = mapping
            self._restart()

    def _restart(self) -> None:
        if self._listener:
            self._listener.stop()
        hotkey_map = {format_combo(v): (lambda action=k: self.dispatcher(action)) for k, v in self.mapping.items() if len(v) >= 2}
        if hotkey_map:
            self._listener = keyboard.GlobalHotKeys(hotkey_map)
            self._listener.start()
        else:
            self._listener = None


def capture_hotkey_blocking(min_keys: int = 2, timeout: int = 10) -> Optional[List[str]]:
    combo: List[str] = []
    done = threading.Event()

    def on_press(key: keyboard.Key | keyboard.KeyCode) -> None:
        label = key.char if isinstance(key, keyboard.KeyCode) and key.char else f"<{key.name}>"
        if label and label not in combo:
            combo.append(label)

    def on_release(_key: keyboard.Key | keyboard.KeyCode) -> bool | None:
        if len(combo) >= min_keys:
            done.set()
            return False
        return None

    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()
    done.wait(timeout=timeout)
    listener.stop()
    listener.join()
    if len(combo) >= min_keys:
        return combo
    return None

