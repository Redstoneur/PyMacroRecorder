"""Utility helpers for key/button normalization and formatting."""

from __future__ import annotations

from typing import Iterable, List, Set

from pynput import keyboard, mouse


def key_to_str(key: keyboard.Key | keyboard.KeyCode) -> str:
    """Normalize a pynput key to string label.

    :param key: Key instance from pynput.
    :type key: keyboard.Key | keyboard.KeyCode
    :return: Normalized key label.
    :rtype: str
    """
    if isinstance(key, keyboard.KeyCode):
        if key.char:
            return key.char
        if key.vk is not None:
            return f"<vk_{key.vk}>"
        return ""
    return f"<{key.name}>" if key.name else ""


def button_to_str(btn: mouse.Button) -> str:
    """Normalize a mouse button to string label.

    :param btn: Mouse button instance.
    :type btn: mouse.Button
    :return: Button label.
    :rtype: str
    """
    return btn.name if hasattr(btn, "name") else str(btn)


def normalize_label(label: str) -> str:
    """Normalize an individual key label for parsing.

    :param label: Raw label such as ``<ctrl>`` or ``A``.
    :type label: str
    :return: Normalized lowercase label.
    :rtype: str
    """
    if label.startswith("<") and label.endswith(">"):
        inner = label[1:-1]
        if inner.startswith("vk_"):
            try:
                vk = int(inner.replace("vk_", ""))
            except ValueError:
                return label
            if 0x30 <= vk <= 0x39:  # digits
                return chr(vk)
            if 0x41 <= vk <= 0x5A:  # letters A-Z
                return chr(vk + 32)  # lower-case alpha for pynput parser
        return f"<{inner.lower()}>"
    if len(label) == 1:
        return label.lower()
    return label


def normalize_combo(combo: Iterable[str]) -> List[str]:
    """Normalize each label in a hotkey combination.

    :param combo: Iterable of key labels.
    :type combo: Iterable[str]
    :return: Normalized labels preserving order.
    :rtype: list[str]
    """
    return [normalize_label(x) for x in combo]


def is_parseable_hotkey(combo_str: str) -> bool:
    """Return whether a combo string can be parsed by pynput.

    :param combo_str: Hotkey combination string (e.g., ``<ctrl>+c``).
    :type combo_str: str
    :return: ``True`` if parsable, otherwise ``False``.
    :rtype: bool
    """
    try:
        keyboard.HotKey.parse(combo_str)
        return True
    except Exception:
        return False


def str_to_key(label: str) -> keyboard.Key | keyboard.KeyCode:
    """Convert a normalized label to a pynput key instance.

    :param label: Normalized label such as ``a`` or ``<ctrl>``.
    :type label: str
    :return: Corresponding pynput key or keycode.
    :rtype: keyboard.Key | keyboard.KeyCode
    """
    if not label:
        return keyboard.KeyCode.from_char(" ")
    if label.startswith("<") and label.endswith(">"):
        name = label[1:-1]
        if name.startswith("vk_"):
            try:
                return keyboard.KeyCode.from_vk(int(name.replace("vk_", "")))
            except ValueError:
                return keyboard.KeyCode.from_char(" ")
        try:
            return keyboard.Key[name]
        except KeyError:
            return keyboard.KeyCode.from_char(name[0])
    if len(label) == 1:
        return keyboard.KeyCode.from_char(label)
    # Fallback: take first char to avoid crashes on invalid labels
    return keyboard.KeyCode.from_char(label[0])


def str_to_button(label: str) -> mouse.Button:
    """Convert a normalized label to a pynput mouse button.

    :param label: Normalized button label.
    :type label: str
    :return: Mouse button enum value.
    :rtype: mouse.Button
    """
    try:
        return mouse.Button[label]
    except KeyError:
        try:
            return mouse.Button(int(label))  # handle numeric value
        except Exception:
            return mouse.Button.left


def format_combo(combo: Iterable[str]) -> str:
    """Join a combo into a ``+`` separated string.

    :param combo: Normalized labels.
    :type combo: Iterable[str]
    :return: Joined combination string.
    :rtype: str
    """
    return "+".join(combo)


def combos_as_sets(mapping: Iterable[List[str]]) -> List[Set[str]]:
    """Convert a list of combos to list of sets for fast comparison.

    :param mapping: Hotkey combos.
    :type mapping: Iterable[list[str]]
    :return: List of sets for each combo.
    :rtype: list[set[str]]
    """
    return [set(x) for x in mapping]


def pressed_matches_hotkey(pressed: Set[str], hotkeys: List[Set[str]]) -> bool:
    """Check if pressed keys satisfy any hotkey combination.

    :param pressed: Currently pressed key labels.
    :type pressed: set[str]
    :param hotkeys: List of hotkey sets to match against.
    :type hotkeys: list[set[str]]
    :return: ``True`` if a hotkey is matched.
    :rtype: bool
    """
    return any(hk.issubset(pressed) for hk in hotkeys)
