"""Utility helpers for key/button normalization and formatting."""

from __future__ import annotations

from typing import Iterable, List, Set

from pynput import keyboard, mouse


def key_to_str(key: keyboard.Key | keyboard.KeyCode) -> str:
    if isinstance(key, keyboard.KeyCode):
        if key.char:
            return key.char
        if key.vk is not None:
            return f"<vk_{key.vk}>"
        return ""
    return f"<{key.name}>" if key.name else ""


def button_to_str(btn: mouse.Button) -> str:
    return btn.name if hasattr(btn, "name") else str(btn)


def str_to_key(label: str) -> keyboard.Key | keyboard.KeyCode:
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
    try:
        return mouse.Button[label]
    except KeyError:
        try:
            return mouse.Button(int(label))  # handle numeric value
        except Exception:
            return mouse.Button.left


def format_combo(combo: Iterable[str]) -> str:
    return "+".join(combo)


def combos_as_sets(mapping: Iterable[List[str]]) -> List[Set[str]]:
    return [set(x) for x in mapping]


def pressed_matches_hotkey(pressed: Set[str], hotkeys: List[Set[str]]) -> bool:
    return any(hk.issubset(pressed) for hk in hotkeys)
