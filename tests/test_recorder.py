"""Recorder tests (without UI)."""
# pylint: disable=protected-access

import itertools

from pynput import keyboard

from pymacrorecorder.recorder import Recorder



def test_recorder_records_events_with_delay(monkeypatch) -> None:
    """Records events with calculated delay."""
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
    """Returns an empty list if stopped without starting."""
    recorder = Recorder()
    assert not recorder.stop()



def test_recorder_ignores_when_hotkey_pressed() -> None:
    """Ignores events during a hotkey to ignore."""
    recorder = Recorder()
    recorder.start(ignored_hotkeys=[["<ctrl>", "r"]])

    recorder._on_key_press(keyboard.Key["ctrl"])
    recorder._on_key_press(keyboard.KeyCode.from_char("r"))
    recorder._on_click(10, 10, None, True)

    events = recorder.stop()

    assert len(events) == 1
    assert events[0].event_type == "key_down"


def test_recorder_scroll_and_move_events(monkeypatch) -> None:
    """Records scroll and move events."""
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
    """Does not add key_up event when hotkey is active."""
    recorder = Recorder()
    recorder.start(ignored_hotkeys=[["<ctrl>", "r"]])

    recorder._on_key_press(keyboard.Key["ctrl"])
    recorder._on_key_press(keyboard.KeyCode.from_char("r"))
    recorder._on_key_release(keyboard.KeyCode.from_char("r"))

    events = recorder.stop()

    assert len(events) == 1
    assert events[0].event_type == "key_down"



def test_recorder_no_events_when_not_running() -> None:
    """Does not produce events if the recorder is not started."""
    recorder = Recorder()

    recorder._on_move(1, 2)
    recorder._on_scroll(1, 2, 3, 4)

    assert not recorder.stop()
