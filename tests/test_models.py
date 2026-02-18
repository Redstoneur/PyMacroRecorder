"""Tests des modeles de macro."""

from pymacrorecorder.models import Macro, MacroEvent


def test_macro_is_empty() -> None:
    """Verifie l'etat vide ou non d'une macro."""
    assert Macro(name="empty").is_empty() is True
    macro = Macro(name="filled", events=[MacroEvent("key_down", {"key": "a"}, 0)])
    assert macro.is_empty() is False
