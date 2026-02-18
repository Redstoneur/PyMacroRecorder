"""Recorder tests (without UI).

This module tests the Recorder class functionality, including event
recording, delay calculation, hotkey filtering, and event type handling.
"""
# pylint: disable=protected-access

import itertools

from pynput import keyboard

from pymacrorecorder.recorder import Recorder



def test_recorder_records_events_with_delay(monkeypatch) -> None:
    """Records events with calculated delay.

    Verifies that the Recorder correctly captures key press and release
    events with accurate delay calculations based on timestamps.

    :param monkeypatch: Pytest monkeypatch fixture
    :return: None
    :rtype: None
    """
    times = itertools.chain([100.0, 100.1, 100.3], itertools.repeat(100.3))
    monkeypatch.setattr("pymacrorecorder.recorder.time.time", lambda: next(times))

    recorder = Recorder()
    recorder.start(ignored_hotkeys=[])

    key = keyboard.KeyCode.from_char("a")
    recorder._on_key_press(key)
    recorder._on_key_release(key)

    events = recorder.stop()

    assert len(events) == 2
    assert events[0].event_type == "key_down"
    assert events[0].delay_ms == 0
    assert events[1].event_type == "key_up"
    assert events[1].delay_ms == 200



def test_recorder_stop_without_start() -> None:
    """Returns an empty list if stopped without starting.

    Verifies that calling stop() without a prior start() returns
    an empty event list.

    :return: None
    :rtype: None
    """
    recorder = Recorder()
    assert not recorder.stop()



def test_recorder_ignores_when_hotkey_pressed() -> None:
    """Ignores events during a hotkey to ignore.

    Verifies that the Recorder correctly filters out events when
    an ignored hotkey combination is being pressed.

    :return: None
    :rtype: None
    """
    recorder = Recorder()
    recorder.start(ignored_hotkeys=[["<ctrl>", "r"]])

    recorder._on_key_press(keyboard.Key["ctrl"])
    recorder._on_key_press(keyboard.KeyCode.from_char("r"))
    recorder._on_click(10, 10, None, True)

    events = recorder.stop()

    assert len(events) == 1
    assert events[0].event_type == "key_down"


def test_recorder_scroll_and_move_events(monkeypatch) -> None:
    """Records scroll and move events.

    Verifies that the Recorder correctly captures mouse scroll and
    move events with proper payload formatting.

    :param monkeypatch: Pytest monkeypatch fixture
    :return: None
    :rtype: None
    """
    monkeypatch.setattr("pymacrorecorder.recorder.time.time", lambda: 100.0)
    recorder = Recorder()
    recorder.start(ignored_hotkeys=[])

    recorder._on_scroll(10, 20, 1, -1)
    recorder._on_move(30, 40)

    events = recorder.stop()

    assert len(events) == 2
    assert events[0].event_type == "mouse_scroll"
    assert events[0].payload == {"x": 10, "y": 20, "dx": 1, "dy": -1}
    assert events[1].event_type == "mouse_move"
    assert events[1].payload == {"x": 30, "y": 40}



def test_recorder_ignores_release_when_hotkey_active() -> None:
    """Does not add key_up event when hotkey is active.

    Verifies that the Recorder ignores key release events when
    they are part of an active ignored hotkey combination.

    :return: None
    :rtype: None
    """
    recorder = Recorder()
    recorder.start(ignored_hotkeys=[["<ctrl>", "r"]])

    recorder._on_key_press(keyboard.Key["ctrl"])
    recorder._on_key_press(keyboard.KeyCode.from_char("r"))
    recorder._on_key_release(keyboard.KeyCode.from_char("r"))

    events = recorder.stop()

    assert len(events) == 1
    assert events[0].event_type == "key_down"



def test_recorder_no_events_when_not_running() -> None:
    """Does not produce events if the recorder is not started.

    Verifies that event callbacks do not record events when the
    Recorder has not been started.

    :return: None
    :rtype: None
    """
    recorder = Recorder()

    recorder._on_move(1, 2)
    recorder._on_scroll(1, 2, 3, 4)

    assert not recorder.stop()
