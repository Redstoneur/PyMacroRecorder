"""Macro player tests."""
# pylint: disable=protected-access

from pymacrorecorder.models import Macro, MacroEvent
from pymacrorecorder.player import Player


def test_player_applies_events_and_completes(monkeypatch) -> None:
    """Applies events and calls completion."""
    player = Player()
    completed = {"called": False}
    player.on_completion = lambda: completed.update({"called": True})

    macro = Macro(
        name="demo",
        events=[
            MacroEvent("key_down", {"key": "a"}, 0),
            MacroEvent("key_up", {"key": "a"}, 0),
            MacroEvent("mouse_move", {"x": 10, "y": 20}, 0),
            MacroEvent("mouse_scroll", {"x": 0, "y": 0, "dx": 1, "dy": -1}, 0),
            MacroEvent("mouse_click", {"x": 5, "y": 6, "button": "left", "action": "press"}, 0),
            MacroEvent("mouse_click", {"x": 5, "y": 6, "button": "left", "action": "release"}, 0),
        ],
    )

    monkeypatch.setattr("pymacrorecorder.player.time.sleep", lambda _s: None)
    player._run(macro, repeats=1)

    assert completed["called"] is True
    assert player._keyboard.pressed
    assert player._keyboard.released
    assert player._mouse.scrolled


def test_player_stop_prevents_completion(monkeypatch) -> None:
    """Does not trigger completion if stop is requested."""
    player = Player()
    completed = {"called": False}
    player.on_completion = lambda: completed.update({"called": True})

    macro = Macro(
        name="demo",
        events=[MacroEvent("key_down", {"key": "a"}, 0)],
    )

    player._stop_event.set()
    monkeypatch.setattr("pymacrorecorder.player.time.sleep", lambda _s: None)
    player._run(macro, repeats=1)

    assert completed["called"] is False
