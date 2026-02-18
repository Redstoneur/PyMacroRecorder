"""Hotkey manager tests.

This module tests the hotkey management system, including combo filtering,
listener lifecycle, hotkey capture, and event dispatching functionality.
"""
# pylint: disable=too-few-public-methods
# pylint: disable=protected-access

from types import SimpleNamespace

import pymacrorecorder.hotkeys as hotkeys_module
from pymacrorecorder.hotkeys import HotkeyManager, capture_hotkey_blocking


def test_hotkey_manager_filters_and_starts() -> None:
    """Validates combo filtering and dispatcher execution.

    Verifies that HotkeyManager filters invalid hotkey combinations,
    starts the listener with valid combos, and dispatches events correctly.

    :return: None
    :rtype: None
    """
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
    """Does not start listener when the map is empty.

    Verifies that HotkeyManager does not create a listener when
    provided with an empty hotkey mapping.

    :return: None
    :rtype: None
    """
    manager = HotkeyManager(mapping={}, dispatcher=lambda _a: None)

    manager.start()

    assert manager._listener is None


def test_hotkey_manager_stop_clears_listener() -> None:
    """Stops the listener and sets it back to None.

    Verifies that stop() properly terminates the listener and
    clears the internal listener reference.

    :return: None
    :rtype: None
    """
    manager = HotkeyManager(mapping={"start": ["<ctrl>", "r"]}, dispatcher=lambda _a: None)

    manager.start()
    assert manager._listener is not None

    manager.stop()

    assert manager._listener is None


def test_hotkey_manager_update_restarts_listener() -> None:
    """Restarts with a new valid map.

    Verifies that update() stops the old listener and starts a new
    one with the updated hotkey mapping.

    :return: None
    :rtype: None
    """
    manager = HotkeyManager(mapping={"start": ["<ctrl>", "r"]}, dispatcher=lambda _a: None)

    manager.start()
    assert manager._listener is not None

    manager.update({"save": ["<ctrl>", "s"]})

    assert manager._listener is not None
    assert "<ctrl>+s" in manager._listener.mapping


def test_capture_hotkey_blocking_returns_combo(monkeypatch) -> None:
    """Captures a valid combination and normalizes it.

    Verifies that capture_hotkey_blocking correctly captures keypresses,
    normalizes the combination, and returns it after key release.

    :param monkeypatch: Pytest monkeypatch fixture
    :return: None
    :rtype: None
    """

    class FakeEvent:
        """Fake threading event for testing.

        Simulates threading.Event for coordinating key capture completion.
        """

        def __init__(self) -> None:
            """Initializes the fake event.

            Sets up the event flag tracking.
            """
            self._set = False

        def set(self) -> None:
            """Sets the event flag.

            :return: None
            :rtype: None
            """
            self._set = True

        def wait(self, _timeout: int | None = None, **_kwargs) -> bool:
            """Waits for the event.

            :param _timeout: Timeout in seconds (ignored)
            :type _timeout: int | None
            :param _kwargs: Additional arguments (ignored)
            :return: Always True
            :rtype: bool
            """
            return True

    class FakeListener:
        """Fake keyboard listener for testing.

        Simulates pynput keyboard listener for capturing key events.
        """

        def __init__(self, on_press, on_release) -> None:
            """Initializes the fake listener.

            :param on_press: Callback for key press events
            :param on_release: Callback for key release events
            """
            self._on_press = on_press
            self._on_release = on_release

        def start(self) -> None:
            """Starts the listener and simulates key events.

            Simulates pressing Ctrl+R for testing purposes.

            :return: None
            :rtype: None
            """
            self._on_press(hotkeys_module.keyboard.Key.ctrl)
            self._on_press(hotkeys_module.keyboard.KeyCode.from_char("r"))
            self._on_release(hotkeys_module.keyboard.KeyCode.from_char("r"))

        def stop(self) -> None:
            """Stops the listener.

            :return: None
            :rtype: None
            """
            return None

        def join(self) -> None:
            """Joins the listener thread.

            :return: None
            :rtype: None
            """
            return None

    monkeypatch.setattr(hotkeys_module, "threading", SimpleNamespace(Event=FakeEvent))
    monkeypatch.setattr(hotkeys_module.keyboard, "Listener", FakeListener)

    combo = capture_hotkey_blocking(min_keys=2, timeout=1)

    assert combo == ["<ctrl>", "r"]


def test_capture_hotkey_blocking_returns_none_when_too_short(monkeypatch) -> None:
    """Returns None if the combination is too short.

    Verifies that capture_hotkey_blocking returns None when the
    captured key combination has fewer keys than the required minimum.

    :param monkeypatch: Pytest monkeypatch fixture
    :return: None
    :rtype: None
    """

    class FakeEvent:
        """Fake threading event for testing.

        Simulates threading.Event for coordinating key capture completion.
        """

        def wait(self, _timeout: int | None = None, **_kwargs) -> bool:
            """Waits for the event.

            :param _timeout: Timeout in seconds (ignored)
            :type _timeout: int | None
            :param _kwargs: Additional arguments (ignored)
            :return: Always True
            :rtype: bool
            """
            return True

    class FakeListener:
        """Fake keyboard listener for testing.

        Simulates pynput keyboard listener with insufficient key presses.
        """

        def __init__(self, on_press, on_release) -> None:
            """Initializes the fake listener.

            :param on_press: Callback for key press events
            :param on_release: Callback for key release events
            """
            self._on_press = on_press
            self._on_release = on_release

        def start(self) -> None:
            """Starts the listener and simulates key events.

            Simulates pressing only 'x' key (insufficient for min_keys=2).

            :return: None
            :rtype: None
            """
            self._on_press(hotkeys_module.keyboard.KeyCode.from_char("x"))
            self._on_release(hotkeys_module.keyboard.KeyCode.from_char("x"))

        def stop(self) -> None:
            """Stops the listener.

            :return: None
            :rtype: None
            """
            return None

        def join(self) -> None:
            """Joins the listener thread.

            :return: None
            :rtype: None
            """
            return None

    monkeypatch.setattr(hotkeys_module, "threading", SimpleNamespace(Event=FakeEvent))
    monkeypatch.setattr(hotkeys_module.keyboard, "Listener", FakeListener)

    combo = capture_hotkey_blocking(min_keys=2, timeout=1)

    assert combo is None
