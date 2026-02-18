"""Tests des utilitaires clavier/souris."""

from pynput import keyboard, mouse

from pymacrorecorder import utils


def test_key_to_str_with_keycode_char() -> None:
    """Convertit un KeyCode en label."""
    key = keyboard.KeyCode.from_char("a")
    assert utils.key_to_str(key) == "a"


def test_key_to_str_with_keycode_vk() -> None:
    """Convertit un KeyCode VK en label."""
    key = keyboard.KeyCode(vk=65)
    assert utils.key_to_str(key) == "<vk_65>"


def test_key_to_str_with_special_key() -> None:
    """Convertit une touche speciale en label."""
    assert utils.key_to_str(keyboard.Key.enter) == "<enter>"


def test_normalize_label_variants() -> None:
    """Normalise differents formats de label."""
    assert utils.normalize_label("A") == "a"
    assert utils.normalize_label("<CTRL>") == "<ctrl>"
    assert utils.normalize_label("<vk_50>") == "2"
    assert utils.normalize_label("<vk_65>") == "a"


def test_is_parseable_hotkey() -> None:
    """Valide une combinaison parseable."""
    assert utils.is_parseable_hotkey("<ctrl>+c") is True
    assert utils.is_parseable_hotkey("not+a+hotkey") is False


def test_str_to_key_variants() -> None:
    """Convertit un label en Key/KeyCode."""
    assert utils.str_to_key("").char == " "
    assert utils.str_to_key("<ctrl>") == keyboard.Key.ctrl
    assert utils.str_to_key("<vk_65>").vk == 65
    assert utils.str_to_key("x").char == "x"
    assert utils.str_to_key("bad").char == "b"


def test_str_to_button_variants() -> None:
    """Convertit un label en bouton souris."""
    assert utils.str_to_button("left") == mouse.Button.left
    assert utils.str_to_button("invalid") == mouse.Button.left


def test_format_and_match_helpers() -> None:
    """Teste les helpers de format/match."""
    combo = ["<ctrl>", "c"]
    assert utils.format_combo(combo) == "<ctrl>+c"
    hotkeys = utils.combos_as_sets([combo])
    assert utils.pressed_matches_hotkey({"<ctrl>", "c"}, hotkeys) is True
