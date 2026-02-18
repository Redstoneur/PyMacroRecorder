"""Macro model tests."""

from pymacrorecorder.models import Macro, MacroEvent


def test_macro_is_empty() -> None:
    """Verifies whether a macro is empty or not."""
    assert Macro(name="empty").is_empty() is True
    macro = Macro(name="filled", events=[MacroEvent("key_down", {"key": "a"}, 0)])
    assert macro.is_empty() is False
