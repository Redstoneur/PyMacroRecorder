"""Macro model tests.

This module tests the Macro and MacroEvent data models, including
macro validation and utility methods.
"""

from pymacrorecorder.models import Macro, MacroEvent


def test_macro_is_empty() -> None:
    """Verifies whether a macro is empty or not.

    Tests the is_empty() method to correctly identify macros with
    no events as empty and macros with events as non-empty.

    :return: None
    :rtype: None
    """
    assert Macro(name="empty").is_empty() is True
    macro = Macro(name="filled", events=[MacroEvent("key_down", {"key": "a"}, 0)])
    assert macro.is_empty() is False
