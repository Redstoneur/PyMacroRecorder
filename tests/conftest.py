"""Fixtures and fakes for headless tests (simulated pynput).

This module provides fake implementations of tkinter and pynput classes
to enable headless testing without requiring actual GUI or input devices.
All fake classes simulate the interface of their real counterparts while
maintaining testability and deterministic behavior.
"""
# pylint: disable=too-few-public-methods

import sys
import types
from enum import Enum
from pathlib import Path


class _FakeWidget:
    """Fake Tkinter widget for headless testing.

    Simulates basic Tkinter widget behavior including geometry management,
    event binding, and configuration without requiring an actual GUI.
    """

    def __init__(self, *_args, **_kwargs) -> None:
        """Initializes the fake widget.

        :param _args: Positional arguments (ignored)
        :param _kwargs: Keyword arguments (ignored)
        """
        self._state = None

    def pack(self, *_args, **_kwargs) -> None:
        """Simulates the pack geometry manager.

        :param _args: Positional arguments (ignored)
        :param _kwargs: Keyword arguments (ignored)
        :return: None
        :rtype: None
        """
        return None

    def grid(self, *_args, **_kwargs) -> None:
        """Simulates the grid geometry manager.

        :param _args: Positional arguments (ignored)
        :param _kwargs: Keyword arguments (ignored)
        :return: None
        :rtype: None
        """
        return None

    def bind(self, *_args, **_kwargs) -> None:
        """Simulates event binding to the widget.

        :param _args: Positional arguments (ignored)
        :param _kwargs: Keyword arguments (ignored)
        :return: None
        :rtype: None
        """
        return None

    def configure(self, **kwargs) -> None:
        """Simulates widget configuration.

        :param kwargs: Configuration options (state is tracked)
        :type kwargs: dict
        :return: None
        :rtype: None
        """
        self._state = kwargs.get("state", self._state)

    def insert(self, *_args, **_kwargs) -> None:
        """Simulates inserting content into the widget.

        :param _args: Positional arguments (ignored)
        :param _kwargs: Keyword arguments (ignored)
        :return: None
        :rtype: None
        """
        return None

    def see(self, *_args, **_kwargs) -> None:
        """Simulates scrolling the widget to make content visible.

        :param _args: Positional arguments (ignored)
        :param _kwargs: Keyword arguments (ignored)
        :return: None
        :rtype: None
        """
        return None

    def column(self, *_args, **_kwargs) -> None:
        """Simulates column configuration for tree widgets.

        :param _args: Positional arguments (ignored)
        :param _kwargs: Keyword arguments (ignored)
        :return: None
        :rtype: None
        """
        return None

    def heading(self, *_args, **_kwargs) -> None:
        """Simulates heading configuration for tree widgets.

        :param _args: Positional arguments (ignored)
        :param _kwargs: Keyword arguments (ignored)
        :return: None
        :rtype: None
        """
        return None

    def delete(self, *_args, **_kwargs) -> None:
        """Simulates deletion of items from the widget.

        :param _args: Positional arguments (ignored)
        :param _kwargs: Keyword arguments (ignored)
        :return: None
        :rtype: None
        """
        return None

    def get_children(self) -> list:
        """Returns fake children list.

        :return: Empty list of children
        :rtype: list
        """
        return []

    def selection(self) -> list:
        """Returns fake selection.

        :return: Empty list representing no selection
        :rtype: list
        """
        return []

    def index(self, _item) -> int:
        """Returns fake item index.

        :param _item: Item to get index for (ignored)
        :return: Always returns 0
        :rtype: int
        """
        return 0


class _FakeTk(_FakeWidget):
    """Fake Tkinter root window for headless testing.

    Extends _FakeWidget with root window specific methods like mainloop,
    title, geometry, and icon management.
    """

    def after(self, *_args, **_kwargs) -> None:
        """Simulates scheduling a callback after a delay.

        :param _args: Positional arguments (ignored)
        :param _kwargs: Keyword arguments (ignored)
        :return: None
        :rtype: None
        """
        return None

    def mainloop(self) -> None:
        """Simulates the Tkinter main event loop.

        :return: None
        :rtype: None
        """
        return None

    def title(self, *_args) -> None:
        """Simulates setting the window title.

        :param _args: Title string (ignored)
        :return: None
        :rtype: None
        """
        return None

    def geometry(self, *_args) -> None:
        """Simulates setting the window geometry.

        :param _args: Geometry string (ignored)
        :return: None
        :rtype: None
        """
        return None

    def iconphoto(self, *_args, **_kwargs) -> None:
        """Simulates setting the window icon from a photo image.

        :param _args: Positional arguments (ignored)
        :param _kwargs: Keyword arguments (ignored)
        :return: None
        :rtype: None
        """
        return None

    def iconbitmap(self, *_args, **_kwargs) -> None:
        """Simulates setting the window icon from a bitmap file.

        :param _args: Positional arguments (ignored)
        :param _kwargs: Keyword arguments (ignored)
        :return: None
        :rtype: None
        """
        return None


class _FakeStringVar:
    """Fake Tkinter StringVar for headless testing.

    Simulates a Tkinter StringVar variable that holds a string value.
    """

    def __init__(self, value: str = "") -> None:
        """Initializes the fake StringVar.

        :param value: Initial string value
        :type value: str
        """
        self._value = value

    def get(self) -> str:
        """Returns the stored string value.

        :return: Current string value
        :rtype: str
        """
        return self._value

    def set(self, value: str) -> None:
        """Sets the string value.

        :param value: New string value to set
        :type value: str
        :return: None
        :rtype: None
        """
        self._value = value


class _FakePhotoImage:
    """Fake Tkinter PhotoImage for headless testing.

    Simulates a Tkinter PhotoImage without actually loading images.
    """

    def __init__(self, **_kwargs) -> None:
        """Initializes the fake photo image.

        :param _kwargs: Keyword arguments (ignored)
        """


class _FakeEvent:
    """Fake Tkinter Event for headless testing.

    Simulates a Tkinter event object without actual event data.
    """


def _setup_fake_tkinter_modules():
    """Configures fake tkinter modules for headless tests.

    Sets up fake implementations of tkinter, tkinter.ttk, tkinter.filedialog,
    and tkinter.messagebox in sys.modules to enable testing without a display.

    :return: None
    :rtype: None
    """
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
    """Checks if tkinter is available and configures fakes if necessary.

    Attempts to import tkinter, and if it fails (e.g., headless environment),
    sets up fake tkinter modules instead.

    :return: None
    :rtype: None
    """
    try:
        import tkinter as _tkinter  # pylint: disable=import-outside-toplevel
        del _tkinter
    except (ImportError, ModuleNotFoundError):
        _setup_fake_tkinter_modules()


_check_tkinter_available()


class _FakeKey:
    """Fake pynput Key for headless testing.

    Represents a special keyboard key (e.g., ctrl, alt, shift).
    """

    def __init__(self, name: str) -> None:
        """Initializes the fake key.

        :param name: Name of the special key
        :type name: str
        """
        self.name = name


class _FakeKeyEnum:
    """Fake pynput Key enumeration for headless testing.

    Provides access to special keys like ctrl, alt, shift, enter.
    """

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
        """Gets a special key by name.

        :param name: Name of the special key
        :type name: str
        :return: The corresponding fake key
        :rtype: _FakeKey
        """
        return cls._map[name]


class _FakeKeyCode:
    """Fake pynput KeyCode for headless testing.

    Represents a keyboard key with either a character or virtual key code.
    """

    def __init__(self, char: str | None = None, vk: int | None = None) -> None:
        """Initializes the fake key code.

        :param char: Character representation of the key
        :type char: str | None
        :param vk: Virtual key code
        :type vk: int | None
        """
        self.char = char
        self.vk = vk

    @classmethod
    def from_char(cls, char: str):
        """Creates a fake key code from a character.

        :param char: Character to create key from
        :type char: str
        :return: Fake key code instance
        :rtype: _FakeKeyCode
        """
        return cls(char=char, vk=None)

    @classmethod
    def from_vk(cls, vk: int):
        """Creates a fake key code from a virtual key code.

        :param vk: Virtual key code
        :type vk: int
        :return: Fake key code instance
        :rtype: _FakeKeyCode
        """
        return cls(char=None, vk=vk)


class _FakeHotKey:
    """Fake pynput HotKey parser for headless testing.

    Validates hotkey combination strings.
    """

    @staticmethod
    def parse(combo_str: str) -> None:
        """Parses and validates a hotkey combination string.

        :param combo_str: Hotkey combination string (e.g., "<ctrl>+c")
        :type combo_str: str
        :return: None
        :rtype: None
        :raises ValueError: If the hotkey format is invalid
        """
        if not combo_str or "+" not in combo_str:
            raise ValueError("Invalid hotkey")
        for part in combo_str.split("+"):
            if part.startswith("<") and part.endswith(">"):
                continue
            if len(part) == 1:
                continue
            raise ValueError("Invalid hotkey")


class _BaseListener:
    """Fake base listener for headless testing.

    Simulates pynput listener behavior without actual input monitoring.
    """

    def __init__(self, **_kwargs) -> None:
        """Initializes the fake listener.

        :param _kwargs: Keyword arguments (ignored)
        """
        self.started = False

    def start(self) -> None:
        """Simulates listener start.

        :return: None
        :rtype: None
        """
        self.started = True

    def stop(self) -> None:
        """Simulates listener stop.

        :return: None
        :rtype: None
        """
        self.started = False

    def join(self) -> None:
        """Simulates joining the listener thread.

        :return: None
        :rtype: None
        """
        return None


class _FakeGlobalHotKeys:
    """Fake pynput GlobalHotKeys listener for headless testing.

    Simulates global hotkey monitoring without actual keyboard hooks.
    """

    def __init__(self, mapping: dict) -> None:
        """Initializes the fake global hotkeys listener.

        :param mapping: Dictionary mapping hotkey strings to callbacks
        :type mapping: dict
        """
        self.mapping = mapping
        self.started = False

    def start(self) -> None:
        """Simulates global hotkeys listener start.

        :return: None
        :rtype: None
        """
        self.started = True

    def stop(self) -> None:
        """Simulates global hotkeys listener stop.

        :return: None
        :rtype: None
        """
        self.started = False


class _FakeKeyboardController:
    """Fake pynput keyboard controller for headless testing.

    Tracks simulated key presses and releases without actual keyboard events.
    """

    def __init__(self) -> None:
        """Initializes the fake keyboard controller.

        Records of pressed and released keys are stored in lists.
        """
        self.pressed = []
        self.released = []

    def press(self, key) -> None:
        """Simulates a key press.

        :param key: Key to press
        :return: None
        :rtype: None
        """
        self.pressed.append(key)

    def release(self, key) -> None:
        """Simulates a key release.

        :param key: Key to release
        :return: None
        :rtype: None
        """
        self.released.append(key)


class _FakeMouseButton(Enum):
    """Fake pynput mouse button enumeration for headless testing.

    Provides mouse button constants (left, right).
    """

    left = 1  # pylint: disable=invalid-name
    right = 2  # pylint: disable=invalid-name


class _FakeMouseController:
    """Fake pynput mouse controller for headless testing.

    Tracks simulated mouse actions without actual mouse events.
    """

    def __init__(self) -> None:
        """Initializes the fake mouse controller.

        Tracks position, pressed buttons, released buttons, and scroll events.
        """
        self.position = (0, 0)
        self.pressed = []
        self.released = []
        self.scrolled = []

    def press(self, button) -> None:
        """Simulates a mouse button press.

        :param button: Mouse button to press
        :return: None
        :rtype: None
        """
        self.pressed.append(button)

    def release(self, button) -> None:
        """Simulates a mouse button release.

        :param button: Mouse button to release
        :return: None
        :rtype: None
        """
        self.released.append(button)

    def scroll(self, dx: int, dy: int) -> None:
        """Simulates a mouse scroll.

        :param dx: Horizontal scroll delta
        :type dx: int
        :param dy: Vertical scroll delta
        :type dy: int
        :return: None
        :rtype: None
        """
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
