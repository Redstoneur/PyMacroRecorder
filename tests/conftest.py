"""Fixtures and fakes for headless tests (simulated pynput)."""
# pylint: disable=too-few-public-methods

import sys
import types
from enum import Enum
from pathlib import Path


class _FakeWidget:
    def __init__(self, *_args, **_kwargs) -> None:
        self._state = None

    def pack(self, *_args, **_kwargs) -> None:
        """Simulates pack geometry manager."""
        return None

    def grid(self, *_args, **_kwargs) -> None:
        """Simulates grid geometry manager."""
        return None

    def bind(self, *_args, **_kwargs) -> None:
        """Simulates event binding."""
        return None

    def configure(self, **kwargs) -> None:
        """Simulates widget configuration."""
        self._state = kwargs.get("state", self._state)

    def insert(self, *_args, **_kwargs) -> None:
        """Simulates inserting content."""
        return None

    def see(self, *_args, **_kwargs) -> None:
        """Simulates scrolling to view."""
        return None

    def column(self, *_args, **_kwargs) -> None:
        """Simulates column configuration."""
        return None

    def heading(self, *_args, **_kwargs) -> None:
        """Simulates heading configuration."""
        return None

    def delete(self, *_args, **_kwargs) -> None:
        """Simulates deletion of items."""
        return None

    def get_children(self) -> list:
        """Returns fake children list."""
        return []

    def selection(self) -> list:
        """Returns fake selection."""
        return []

    def index(self, _item) -> int:
        """Returns fake item index."""
        return 0


class _FakeTk(_FakeWidget):
    def after(self, *_args, **_kwargs) -> None:
        """Simulates after scheduling."""
        return None

    def mainloop(self) -> None:
        """Simulates tkinter mainloop."""
        return None

    def title(self, *_args) -> None:
        """Simulates window title."""
        return None

    def geometry(self, *_args) -> None:
        """Simulates window geometry."""
        return None

    def iconphoto(self, *_args, **_kwargs) -> None:
        """Simulates icon photo."""
        return None

    def iconbitmap(self, *_args, **_kwargs) -> None:
        """Simulates icon bitmap."""
        return None


class _FakeStringVar:
    def __init__(self, value: str = "") -> None:
        self._value = value

    def get(self) -> str:
        """Returns the stored string value."""
        return self._value

    def set(self, value: str) -> None:
        """Sets the string value."""
        self._value = value


class _FakePhotoImage:
    def __init__(self, **_kwargs) -> None:
        pass


class _FakeEvent:
    pass


def _setup_fake_tkinter_modules():
    """Configures fake tkinter modules for headless tests."""
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


def _check_tkinter_available():
    """Checks if tkinter is available and configures fakes if necessary."""
    try:
        import tkinter as _tkinter  # pylint: disable=import-outside-toplevel
        del _tkinter
    except (ImportError, ModuleNotFoundError):
        _setup_fake_tkinter_modules()


_check_tkinter_available()


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
        """Creates a fake key code from character."""
        return cls(char=char, vk=None)

    @classmethod
    def from_vk(cls, vk: int):
        """Creates a fake key code from virtual key."""
        return cls(char=None, vk=vk)


class _FakeHotKey:
    @staticmethod
    def parse(combo_str: str) -> None:
        """Parses and validates a hotkey combination string."""
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
        """Simulates listener start."""
        self.started = True

    def stop(self) -> None:
        """Simulates listener stop."""
        self.started = False

    def join(self) -> None:
        """Simulates joining the listener thread."""
        return None


class _FakeGlobalHotKeys:
    def __init__(self, mapping: dict) -> None:
        self.mapping = mapping
        self.started = False

    def start(self) -> None:
        """Simulates global hotkeys listener start."""
        self.started = True

    def stop(self) -> None:
        """Simulates global hotkeys listener stop."""
        self.started = False


class _FakeKeyboardController:
    def __init__(self) -> None:
        self.pressed = []
        self.released = []

    def press(self, key) -> None:
        """Simulates key press."""
        self.pressed.append(key)

    def release(self, key) -> None:
        """Simulates key release."""
        self.released.append(key)


class _FakeMouseButton(Enum):
    left = 1  # pylint: disable=invalid-name
    right = 2  # pylint: disable=invalid-name


class _FakeMouseController:
    def __init__(self) -> None:
        self.position = (0, 0)
        self.pressed = []
        self.released = []
        self.scrolled = []

    def press(self, button) -> None:
        """Simulates mouse button press."""
        self.pressed.append(button)

    def release(self, button) -> None:
        """Simulates mouse button release."""
        self.released.append(button)

    def scroll(self, dx: int, dy: int) -> None:
        """Simulates mouse scroll."""
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
