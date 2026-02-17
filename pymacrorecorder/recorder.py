"""Global recorder for keyboard and mouse events."""

from __future__ import annotations

import threading
import time
from typing import Callable, List, Optional, Set

from pynput import keyboard, mouse

from .models import MacroEvent
from .utils import button_to_str, key_to_str, pressed_matches_hotkey, combos_as_sets

LogFn = Callable[[str], None]


class Recorder:
    """Capture keyboard and mouse events while respecting ignored hotkeys."""

    def __init__(self, log_fn: Optional[LogFn] = None) -> None:
        """Initialize recorder with optional logger.

        :param log_fn: Callback for status messages.
        :type log_fn: Callable[[str], None] | None
        :return: Nothing.
        :rtype: None
        """
        self.log = log_fn or (lambda _: None)
        self._keyboard_listener: Optional[keyboard.Listener] = None
        self._mouse_listener: Optional[mouse.Listener] = None
        self._last_time: float = 0.0
        self._events: List[MacroEvent] = []
        self._running = threading.Event()
        self._pressed: Set[str] = set()
        self._hotkeys: List[Set[str]] = []

    def start(self, ignored_hotkeys: List[List[str]]) -> None:
        """Start recording, ignoring events that match provided hotkeys.

        :param ignored_hotkeys: List of hotkey combos that should not be recorded.
        :type ignored_hotkeys: list[list[str]]
        :return: Nothing.
        :rtype: None
        """
        if self._running.is_set():
            return
        self._hotkeys = combos_as_sets(ignored_hotkeys)
        self._events = []
        self._last_time = time.time()
        self._running.set()
        self._pressed.clear()
        self._keyboard_listener = keyboard.Listener(
            on_press=self._on_key_press, on_release=self._on_key_release
        )
        self._mouse_listener = mouse.Listener(
            on_click=self._on_click, on_scroll=self._on_scroll, on_move=self._on_move
        )
        self._keyboard_listener.start()
        self._mouse_listener.start()
        self.log("Recording started")

    def stop(self) -> List[MacroEvent]:
        """Stop recording and return collected macro events.

        :return: Recorded macro events in order.
        :rtype: list[MacroEvent]
        """
        if not self._running.is_set():
            return []
        self._running.clear()
        if self._keyboard_listener:
            self._keyboard_listener.stop()
            self._keyboard_listener = None
        if self._mouse_listener:
            self._mouse_listener.stop()
            self._mouse_listener = None
        self.log(f"Recording stopped ({len(self._events)} events)")
        return list(self._events)

    def _add_event(self, event_type: str, payload: dict) -> None:
        """Append a macro event with computed delay.

        :param event_type: Identifier for the event type.
        :type event_type: str
        :param payload: Event-specific payload data.
        :type payload: dict
        :return: Nothing.
        :rtype: None
        """
        now = time.time()
        delay_ms = 0 if not self._events else int((now - self._last_time) * 1000)
        self._last_time = now
        self._events.append(MacroEvent(event_type=event_type, payload=payload, delay_ms=delay_ms))

    def _should_ignore(self, pressed_snapshot: Set[str]) -> bool:
        """Return whether current pressed keys match any ignored hotkey.

        :param pressed_snapshot: Current pressed key labels.
        :type pressed_snapshot: set[str]
        :return: ``True`` if event should be ignored.
        :rtype: bool
        """
        return pressed_matches_hotkey(pressed_snapshot, self._hotkeys)

    def _on_key_press(self, key: keyboard.Key | keyboard.KeyCode) -> None:
        """Handle key press events and store them when recording.

        :param key: Pressed key instance.
        :type key: keyboard.Key | keyboard.KeyCode
        :return: Nothing.
        :rtype: None
        """
        if not self._running.is_set():
            return
        label = key_to_str(key)
        self._pressed.add(label)
        if self._should_ignore(self._pressed):
            return
        self._add_event("key_down", {"key": label})

    def _on_key_release(self, key: keyboard.Key | keyboard.KeyCode) -> None:
        """Handle key release events and store them when recording.

        :param key: Released key instance.
        :type key: keyboard.Key | keyboard.KeyCode
        :return: Nothing.
        :rtype: None
        """
        if not self._running.is_set():
            return
        label = key_to_str(key)
        if self._should_ignore(self._pressed):
            self._pressed.discard(label)
            return
        self._add_event("key_up", {"key": label})
        self._pressed.discard(label)

    def _on_click(self, x: int, y: int, button: mouse.Button, pressed: bool) -> None:
        """Record mouse click events.

        :param x: Cursor X coordinate.
        :type x: int
        :param y: Cursor Y coordinate.
        :type y: int
        :param button: Mouse button pressed or released.
        :type button: mouse.Button
        :param pressed: ``True`` if pressed, ``False`` if released.
        :type pressed: bool
        :return: Nothing.
        :rtype: None
        """
        if not self._running.is_set():
            return
        if self._should_ignore(self._pressed):
            return
        self._add_event(
            "mouse_click",
            {
                "x": x,
                "y": y,
                "button": button_to_str(button),
                "action": "press" if pressed else "release"
            }
        )

    def _on_scroll(self, x: int, y: int, dx: int, dy: int) -> None:
        """Record mouse scroll events.

        :param x: Cursor X coordinate.
        :type x: int
        :param y: Cursor Y coordinate.
        :type y: int
        :param dx: Horizontal scroll delta.
        :type dx: int
        :param dy: Vertical scroll delta.
        :type dy: int
        :return: Nothing.
        :rtype: None
        """
        if not self._running.is_set():
            return
        if self._should_ignore(self._pressed):
            return
        self._add_event("mouse_scroll", {"x": x, "y": y, "dx": dx, "dy": dy})

    def _on_move(self, x: int, y: int) -> None:
        """Record mouse move events.

        :param x: Cursor X coordinate.
        :type x: int
        :param y: Cursor Y coordinate.
        :type y: int
        :return: Nothing.
        :rtype: None
        """
        if not self._running.is_set():
            return
        if self._should_ignore(self._pressed):
            return
        self._add_event("mouse_move", {"x": x, "y": y})
