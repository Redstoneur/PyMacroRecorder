"""Global hotkey management."""

from __future__ import annotations

import threading
from typing import Callable, Dict, List, Optional

from pynput import keyboard

from .utils import format_combo, is_parseable_hotkey, key_to_str, normalize_combo

HotkeyCallback = Callable[[str], None]


class HotkeyManager:
    """Manage global hotkey registration and dispatch via pynput."""

    def __init__(self, mapping: Dict[str, List[str]], dispatcher: HotkeyCallback):
        """Create a hotkey manager with an action-to-combo mapping.

        :param mapping: Hotkey mapping keyed by action name.
        :type mapping: dict[str, list[str]]
        :param dispatcher: Callback invoked with action identifier when triggered.
        :type dispatcher: Callable[[str], None]
        :return: Nothing.
        :rtype: None
        """
        self.mapping = mapping
        self.dispatcher = dispatcher
        self._listener: Optional[keyboard.GlobalHotKeys] = None
        self._lock = threading.Lock()

    def start(self) -> None:
        """Start the hotkey listener with the current mapping.

        :return: Nothing.
        :rtype: None
        """
        with self._lock:
            self._restart()

    def stop(self) -> None:
        """Stop the hotkey listener if it is running.

        :return: Nothing.
        :rtype: None
        """
        with self._lock:
            if self._listener:
                self._listener.stop()
                self._listener = None

    def update(self, mapping: Dict[str, List[str]]) -> None:
        """Replace the mapping and restart the listener safely.

        :param mapping: New hotkey mapping keyed by action name.
        :type mapping: dict[str, list[str]]
        :return: Nothing.
        :rtype: None
        """
        with self._lock:
            self.mapping = mapping
            self._restart()

    def _restart(self) -> None:
        """Rebuild the pynput listener according to the current mapping.

        :return: Nothing.
        :rtype: None
        """
        if self._listener:
            self._listener.stop()
        hotkey_map: Dict[str, Callable[[], None]] = {}
        for action, combo in self.mapping.items():
            if len(combo) < 2:
                continue
            normalized = normalize_combo(combo)
            combo_str = format_combo(normalized)
            if not is_parseable_hotkey(combo_str):
                continue
            hotkey_map[combo_str] = lambda action=action: self.dispatcher(action)
        if hotkey_map:
            self._listener = keyboard.GlobalHotKeys(hotkey_map)
            self._listener.start()
        else:
            self._listener = None


def capture_hotkey_blocking(min_keys: int = 2, timeout: int = 10) -> Optional[List[str]]:
    """Capture a hotkey combination synchronously using pynput listeners.

    :param min_keys: Minimum number of keys required to accept the combo.
    :type min_keys: int
    :param timeout: Maximum seconds to wait before aborting capture.
    :type timeout: int
    :return: Normalized combo if enough keys were pressed, else ``None``.
    :rtype: list[str] | None
    """
    combo: List[str] = []
    done = threading.Event()

    def on_press(key: keyboard.Key | keyboard.KeyCode) -> None:
        label = key_to_str(key)
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
        return normalize_combo(combo)
    return None
