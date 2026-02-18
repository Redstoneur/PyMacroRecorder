"""Fixtures et fakes pour tests headless (pynput simulé)."""

# pylint: disable=too-few-public-methods,missing-function-docstring,invalid-name

import sys
import types
from enum import Enum
from pathlib import Path

try:
    import tkinter as _tkinter
    del _tkinter
except (ImportError, ModuleNotFoundError):
    class _FakeWidget:
        def __init__(self, *_args, **_kwargs) -> None:
            self._state = None

        def pack(self, *_args, **_kwargs) -> None:
            return None

        def grid(self, *_args, **_kwargs) -> None:
            return None

        def bind(self, *_args, **_kwargs) -> None:
            return None

        def configure(self, **kwargs) -> None:
            self._state = kwargs.get("state", self._state)

        def insert(self, *_args, **_kwargs) -> None:
            return None

        def see(self, *_args, **_kwargs) -> None:
            return None

        def column(self, *_args, **_kwargs) -> None:
            return None

        def heading(self, *_args, **_kwargs) -> None:
            return None

        def delete(self, *_args, **_kwargs) -> None:
            return None

        def get_children(self) -> list:
            return []

        def selection(self) -> list:
            return []

        def index(self, _item) -> int:
            return 0

    class _FakeTk(_FakeWidget):
        def after(self, *_args, **_kwargs) -> None:
            return None

        def mainloop(self) -> None:
            return None

        def title(self, *_args) -> None:
            return None

        def geometry(self, *_args) -> None:
            return None

        def iconphoto(self, *_args, **_kwargs) -> None:
            return None

        def iconbitmap(self, *_args, **_kwargs) -> None:
            return None

    class _FakeStringVar:
        def __init__(self, value: str = "") -> None:
            self._value = value

        def get(self) -> str:
            return self._value

        def set(self, value: str) -> None:
            self._value = value

    class _FakePhotoImage:
        def __init__(self, **_kwargs) -> None:
            return None

    class _FakeEvent:
        pass

    _fake_ttk = types.SimpleNamespace(
        Frame=_FakeWidget,
        LabelFrame=_FakeWidget,
        Button=_FakeWidget,
        Entry=_FakeWidget,
        Treeview=_FakeWidget,
        Label=_FakeWidget,
    )
    _fake_filedialog = types.SimpleNamespace(
        asksaveasfilename=lambda **_kwargs: "",
        askopenfilename=lambda **_kwargs: "",
    )
    _fake_messagebox = types.SimpleNamespace(
        showwarning=lambda *_args, **_kwargs: None,
        showerror=lambda *_args, **_kwargs: None,
    )
    _fake_tk = types.SimpleNamespace(
        Tk=_FakeTk,
        Label=_FakeWidget,
        Text=_FakeWidget,
        Event=_FakeEvent,
        PhotoImage=_FakePhotoImage,
        StringVar=_FakeStringVar,
        ttk=_fake_ttk,
        filedialog=_fake_filedialog,
        messagebox=_fake_messagebox,
    )
    sys.modules.setdefault("tkinter", _fake_tk)
    sys.modules.setdefault("tkinter.ttk", _fake_ttk)
    sys.modules.setdefault("tkinter.filedialog", _fake_filedialog)
    sys.modules.setdefault("tkinter.messagebox", _fake_messagebox)

class _FakeKey:
    def __init__(self, name: str) -> None:
        self.name = name


class _FakeKeyEnum:
    _map = {
        "ctrl": _FakeKey("ctrl"),
        "alt": _FakeKey("alt"),
        "shift": _FakeKey("shift"),
        "enter": _FakeKey("enter"),
    }

    ctrl = _map["ctrl"]
    alt = _map["alt"]
    shift = _map["shift"]
    enter = _map["enter"]

    def __class_getitem__(cls, name: str):
        return cls._map[name]


class _FakeKeyCode:
    def __init__(self, char: str | None = None, vk: int | None = None) -> None:
        self.char = char
        self.vk = vk

    @classmethod
    def from_char(cls, char: str):
        return cls(char=char, vk=None)

    @classmethod
    def from_vk(cls, vk: int):
        return cls(char=None, vk=vk)


class _FakeHotKey:
    @staticmethod
    def parse(combo_str: str) -> None:
        if not combo_str or "+" not in combo_str:
            raise ValueError("Invalid hotkey")
        for part in combo_str.split("+"):
            if part.startswith("<") and part.endswith(">"):
                continue
            if len(part) == 1:
                continue
            raise ValueError("Invalid hotkey")


class _BaseListener:
    def __init__(self, **_kwargs) -> None:
        self.started = False

    def start(self) -> None:
        self.started = True

    def stop(self) -> None:
        self.started = False

    def join(self) -> None:
        return None


class _FakeGlobalHotKeys:
    def __init__(self, mapping: dict) -> None:
        self.mapping = mapping
        self.started = False

    def start(self) -> None:
        self.started = True

    def stop(self) -> None:
        self.started = False


class _FakeKeyboardController:
    def __init__(self) -> None:
        self.pressed = []
        self.released = []

    def press(self, key) -> None:
        self.pressed.append(key)

    def release(self, key) -> None:
        self.released.append(key)


class _FakeMouseButton(Enum):
    left = 1
    right = 2


class _FakeMouseController:
    def __init__(self) -> None:
        self.position = (0, 0)
        self.pressed = []
        self.released = []
        self.scrolled = []

    def press(self, button) -> None:
        self.pressed.append(button)

    def release(self, button) -> None:
        self.released.append(button)

    def scroll(self, dx: int, dy: int) -> None:
        self.scrolled.append((dx, dy))


_fake_keyboard = types.SimpleNamespace(
    Key=_FakeKeyEnum,
    KeyCode=_FakeKeyCode,
    HotKey=_FakeHotKey,
    Listener=_BaseListener,
    GlobalHotKeys=_FakeGlobalHotKeys,
    Controller=_FakeKeyboardController,
)

_fake_mouse = types.SimpleNamespace(
    Button=_FakeMouseButton,
    Listener=_BaseListener,
    Controller=_FakeMouseController,
)

_fake_pynput = types.SimpleNamespace(
    keyboard=_fake_keyboard,
    mouse=_fake_mouse,
)

sys.modules.setdefault("pynput", _fake_pynput)
sys.modules.setdefault("pynput.keyboard", _fake_keyboard)
sys.modules.setdefault("pynput.mouse", _fake_mouse)

_project_root = Path(__file__).resolve().parents[1]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))
