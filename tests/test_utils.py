"""Keyboard/mouse utility tests."""

from pynput import keyboard, mouse

from pymacrorecorder import utils


def test_key_to_str_with_keycode_char() -> None:
    """Converts a KeyCode to a label."""
    key = keyboard.KeyCode.from_char("a")
    assert utils.key_to_str(key) == "a"


def test_key_to_str_with_keycode_vk() -> None:
    """Converts a VK KeyCode to a label."""
    key = keyboard.KeyCode(vk=65)
    assert utils.key_to_str(key) == "<vk_65>"


def test_key_to_str_with_special_key() -> None:
    """Converts a special key to a label."""
    assert utils.key_to_str(keyboard.Key.enter) == "<enter>"


def test_normalize_label_variants() -> None:
    """Normalizes different label formats."""
    assert utils.normalize_label("A") == "a"
    assert utils.normalize_label("<CTRL>") == "<ctrl>"
    assert utils.normalize_label("<vk_50>") == "2"
    assert utils.normalize_label("<vk_65>") == "a"


def test_is_parseable_hotkey() -> None:
    """Validates a parseable combination."""
    assert utils.is_parseable_hotkey("<ctrl>+c") is True
    assert utils.is_parseable_hotkey("not+a+hotkey") is False


def test_str_to_key_variants() -> None:
    """Converts a label to Key/KeyCode."""
    assert utils.str_to_key("").char == " "
    assert utils.str_to_key("<ctrl>") == keyboard.Key.ctrl
    assert utils.str_to_key("<vk_65>").vk == 65
    assert utils.str_to_key("x").char == "x"
    assert utils.str_to_key("bad").char == "b"


def test_str_to_button_variants() -> None:
    """Converts a label to mouse button."""
    assert utils.str_to_button("left") == mouse.Button.left
    assert utils.str_to_button("invalid") == mouse.Button.left


def test_format_and_match_helpers() -> None:
    """Tests format/match helpers."""
    combo = ["<ctrl>", "c"]
    assert utils.format_combo(combo) == "<ctrl>+c"
    hotkeys = utils.combos_as_sets([combo])
    assert utils.pressed_matches_hotkey({"<ctrl>", "c"}, hotkeys) is True
