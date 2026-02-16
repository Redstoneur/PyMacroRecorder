"""Playback engine for macros."""

from __future__ import annotations

import threading
import time
from typing import Callable, Optional

from pynput import keyboard, mouse

from .models import Macro
from .utils import str_to_button, str_to_key

LogFn = Callable[[str], None]


class Player:
    def __init__(self, log_fn: Optional[LogFn] = None) -> None:
        self.log = log_fn or (lambda _: None)
        self._keyboard = keyboard.Controller()
        self._mouse = mouse.Controller()
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

    def play(self, macro: Macro, repeats: int) -> None:
        if self.is_running():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, args=(macro, repeats), daemon=True)
        self._thread.start()
        self.log(
            f"Playing macro '{macro.name}' (repeats: {'infinite' if repeats == 0 else repeats})"
        )

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        self.log("Playback stopped")

    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def _run(self, macro: Macro, repeats: int) -> None:
        count = 0
        while repeats == 0 or count < repeats:
            if self._stop_event.is_set():
                break
            for event in macro.events:
                if self._stop_event.is_set():
                    break
                time.sleep(max(event.delay_ms / 1000.0, 0))
                self._apply_event(event)
            count += 1
        self._stop_event.clear()

    def _apply_event(self, event) -> None:
        etype = event.event_type
        data = event.payload
        if etype == "key_down":
            self._keyboard.press(str_to_key(data.get("key", "")))
        elif etype == "key_up":
            self._keyboard.release(str_to_key(data.get("key", "")))
        elif etype == "mouse_click":
            button = str_to_button(data.get("button", "left"))
            action = data.get("action", "press")
            x = data.get("x")
            y = data.get("y")
            if x is not None and y is not None:
                self._mouse.position = (x, y)
            if action == "press":
                self._mouse.press(button)
            else:
                self._mouse.release(button)
        elif etype == "mouse_scroll":
            self._mouse.position = (data.get("x", 0), data.get("y", 0))
            self._mouse.scroll(data.get("dx", 0), data.get("dy", 0))
        elif etype == "mouse_move":
            self._mouse.position = (data.get("x", 0), data.get("y", 0))
