"""Hotkey manager tests."""
# pylint: disable=too-few-public-methods
# pylint: disable=protected-access

from types import SimpleNamespace

import pymacrorecorder.hotkeys as hotkeys_module
from pymacrorecorder.hotkeys import HotkeyManager, capture_hotkey_blocking


def test_hotkey_manager_filters_and_starts() -> None:
    """Validates combo filtering and dispatcher execution."""
    dispatched = []
    manager = HotkeyManager(
        mapping={
            "start": ["<ctrl>", "r"],
            "bad": ["x"],
            "invalid": ["<bad>", "xx"],
        },
        dispatcher=dispatched.append,
    )

    manager.start()

    assert manager._listener is not None
    manager._listener.mapping["<ctrl>+r"]()
    assert dispatched == ["start"]


def test_hotkey_manager_update_to_empty() -> None:
    """Does not start listener when the map is empty."""
    manager = HotkeyManager(mapping={}, dispatcher=lambda _a: None)

    manager.start()

    assert manager._listener is None


def test_hotkey_manager_stop_clears_listener() -> None:
    """Stops the listener and sets it back to None."""
    manager = HotkeyManager(mapping={"start": ["<ctrl>", "r"]}, dispatcher=lambda _a: None)

    manager.start()
    assert manager._listener is not None

    manager.stop()

    assert manager._listener is None


def test_hotkey_manager_update_restarts_listener() -> None:
    """Restarts with a new valid map."""
    manager = HotkeyManager(mapping={"start": ["<ctrl>", "r"]}, dispatcher=lambda _a: None)

    manager.start()
    assert manager._listener is not None

    manager.update({"save": ["<ctrl>", "s"]})

    assert manager._listener is not None
    assert "<ctrl>+s" in manager._listener.mapping


def test_capture_hotkey_blocking_returns_combo(monkeypatch) -> None:
    """Captures a valid combination and normalizes it."""

    class FakeEvent:
        """Fake threading event for testing."""

        def __init__(self) -> None:
            self._set = False

        def set(self) -> None:
            """Sets the event flag."""
            self._set = True

        def wait(self, _timeout: int | None = None, **_kwargs) -> bool:
            """Waits for the event."""
            return True

    class FakeListener:
        """Fake keyboard listener for testing."""

        def __init__(self, on_press, on_release) -> None:
            self._on_press = on_press
            self._on_release = on_release

        def start(self) -> None:
            """Starts the listener and simulates key events."""
            self._on_press(hotkeys_module.keyboard.Key.ctrl)
            self._on_press(hotkeys_module.keyboard.KeyCode.from_char("r"))
            self._on_release(hotkeys_module.keyboard.KeyCode.from_char("r"))

        def stop(self) -> None:
            """Stops the listener."""
            return None

        def join(self) -> None:
            """Joins the listener thread."""
            return None

    monkeypatch.setattr(hotkeys_module, "threading", SimpleNamespace(Event=FakeEvent))
    monkeypatch.setattr(hotkeys_module.keyboard, "Listener", FakeListener)

    combo = capture_hotkey_blocking(min_keys=2, timeout=1)

    assert combo == ["<ctrl>", "r"]


def test_capture_hotkey_blocking_returns_none_when_too_short(monkeypatch) -> None:
    """Returns None if the combination is too short."""

    class FakeEvent:
        """Fake threading event for testing."""

        def wait(self, _timeout: int | None = None, **_kwargs) -> bool:
            """Waits for the event."""
            return True

    class FakeListener:
        """Fake keyboard listener for testing."""

        def __init__(self, on_press, on_release) -> None:
            self._on_press = on_press
            self._on_release = on_release

        def start(self) -> None:
            """Starts the listener and simulates key events."""
            self._on_press(hotkeys_module.keyboard.KeyCode.from_char("x"))
            self._on_release(hotkeys_module.keyboard.KeyCode.from_char("x"))

        def stop(self) -> None:
            """Stops the listener."""
            return None

        def join(self) -> None:
            """Joins the listener thread."""
            return None

    monkeypatch.setattr(hotkeys_module, "threading", SimpleNamespace(Event=FakeEvent))
    monkeypatch.setattr(hotkeys_module.keyboard, "Listener", FakeListener)

    combo = capture_hotkey_blocking(min_keys=2, timeout=1)

    assert combo is None
