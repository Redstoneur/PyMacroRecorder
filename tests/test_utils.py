"""Keyboard/mouse utility tests.

This module tests utility functions for keyboard and mouse handling,
including key/button conversions, label normalization, hotkey parsing,
and combination matching.
"""

from pynput import keyboard, mouse

from pymacrorecorder import utils


def test_key_to_str_with_keycode_char() -> None:
    """Converts a KeyCode with char to a label.

    Verifies that key_to_str correctly converts a KeyCode with a
    character attribute to its string representation.

    :return: None
    :rtype: None
    """
    key = keyboard.KeyCode.from_char("a")
    assert utils.key_to_str(key) == "a"


def test_key_to_str_with_keycode_vk() -> None:
    """Converts a VK KeyCode to a label.

    Verifies that key_to_str correctly converts a KeyCode with only
    a virtual key code to a formatted string.

    :return: None
    :rtype: None
    """
    key = keyboard.KeyCode(vk=65)
    assert utils.key_to_str(key) == "<vk_65>"


def test_key_to_str_with_special_key() -> None:
    """Converts a special key to a label.

    Verifies that key_to_str correctly converts special keys
    (e.g., Key.enter) to their formatted string representation.

    :return: None
    :rtype: None
    """
    assert utils.key_to_str(keyboard.Key.enter) == "<enter>"


def test_normalize_label_variants() -> None:
    """Normalizes different label formats.

    Verifies that normalize_label correctly converts labels to
    lowercase and translates virtual key codes to characters.

    :return: None
    :rtype: None
    """
    assert utils.normalize_label("A") == "a"
    assert utils.normalize_label("<CTRL>") == "<ctrl>"
    assert utils.normalize_label("<vk_50>") == "2"
    assert utils.normalize_label("<vk_65>") == "a"


def test_is_parseable_hotkey() -> None:
    """Validates a parseable hotkey combination.

    Verifies that is_parseable_hotkey correctly identifies valid
    and invalid hotkey combination strings.

    :return: None
    :rtype: None
    """
    assert utils.is_parseable_hotkey("<ctrl>+c") is True
    assert utils.is_parseable_hotkey("not+a+hotkey") is False


def test_str_to_key_variants() -> None:
    """Converts a label to Key/KeyCode.

    Verifies that str_to_key correctly converts various string
    representations to Key or KeyCode objects.

    :return: None
    :rtype: None
    """
    assert utils.str_to_key("").char == " "
    assert utils.str_to_key("<ctrl>") == keyboard.Key.ctrl
    assert utils.str_to_key("<vk_65>").vk == 65
    assert utils.str_to_key("x").char == "x"
    assert utils.str_to_key("bad").char == "b"


def test_str_to_button_variants() -> None:
    """Converts a label to mouse button.

    Verifies that str_to_button correctly converts button name
    strings to mouse.Button enum values.

    :return: None
    :rtype: None
    """
    assert utils.str_to_button("left") == mouse.Button.left
    assert utils.str_to_button("invalid") == mouse.Button.left


def test_format_and_match_helpers() -> None:
    """Tests format and match helper functions.

    Verifies that format_combo, combos_as_sets, and
    pressed_matches_hotkey work correctly together for hotkey matching.

    :return: None
    :rtype: None
    """
    combo = ["<ctrl>", "c"]
    assert utils.format_combo(combo) == "<ctrl>+c"
    hotkeys = utils.combos_as_sets([combo])
    assert utils.pressed_matches_hotkey({"<ctrl>", "c"}, hotkeys) is True
