"""Headless tests for Tkinter app utilities.

This module contains comprehensive tests for the App class and its methods,
using fake widgets and components to enable testing without a GUI.
All tests verify app behavior including logging, hotkey handling, macro
management, recording, playback, and file operations.
"""
# pylint: disable=too-few-public-methods
# pylint: disable=protected-access

from pathlib import Path
from types import SimpleNamespace

import pymacrorecorder.app as app_module
from pymacrorecorder.app import App
from pymacrorecorder.models import Macro, MacroEvent


class FakeText:
    """Fake text widget for testing.

    Simulates a Tkinter Text widget with state tracking and content storage.
    """

    def __init__(self) -> None:
        """Initializes the fake text widget.

        Sets up internal state tracking and line storage.
        """
        self.state = None
        self.lines = []

    def configure(self, **kwargs) -> None:
        """Configures the text widget.

        :param kwargs: Configuration options, may include 'state'
        :type kwargs: dict
        :return: None
        :rtype: None
        """
        self.state = kwargs.get("state", self.state)

    def insert(self, _where: str, text: str) -> None:
        """Inserts text into the widget.

        :param _where: Position to insert at (ignored)
        :type _where: str
        :param text: Text content to insert
        :type text: str
        :return: None
        :rtype: None
        """
        self.lines.append(text)

    def see(self, _where: str) -> None:
        """Scrolls to view position.

        :param _where: Position to scroll to (ignored)
        :type _where: str
        :return: None
        :rtype: None
        """
        return None


class FakeLabel:
    """Fake label widget for testing.

    Simulates a Tkinter Label widget with text tracking.
    """

    def __init__(self) -> None:
        """Initializes the fake label widget.

        Sets up internal text storage.
        """
        self.text = ""

    def configure(self, **kwargs) -> None:
        """Configures the label widget.

        :param kwargs: Configuration options, may include 'text'
        :type kwargs: dict
        :return: None
        :rtype: None
        """
        self.text = kwargs.get("text", self.text)


class FakeButton:
    """Fake button widget for testing.

    Simulates a Tkinter Button widget with state tracking.
    """

    def __init__(self) -> None:
        """Initializes the fake button widget.

        Sets up internal state storage.
        """
        self.state = None

    def configure(self, **kwargs) -> None:
        """Configures the button widget.

        :param kwargs: Configuration options, may include 'state'
        :type kwargs: dict
        :return: None
        :rtype: None
        """
        self.state = kwargs.get("state", self.state)


class FakeTreeview:
    """Fake treeview widget for testing.

    Simulates a Tkinter Treeview widget with item and selection management.
    """

    def __init__(self) -> None:
        """Initializes the fake treeview widget.

        Sets up internal item and selection storage.
        """
        self._items = []
        self._selection = []

    def get_children(self):
        """Returns list of child item IDs.

        :return: List of item IDs
        :rtype: list
        """
        return [item["id"] for item in self._items]

    def delete(self, item_id: str) -> None:
        """Deletes an item from the treeview.

        :param item_id: ID of item to delete
        :type item_id: str
        :return: None
        :rtype: None
        """
        self._items = [item for item in self._items if item["id"] != item_id]

    def insert(self, _parent: str, _index: str, values):
        """Inserts a new item into the treeview.

        :param _parent: Parent item ID (ignored)
        :type _parent: str
        :param _index: Position index (ignored)
        :type _index: str
        :param values: Values for the new item
        :return: ID of the inserted item
        :rtype: str
        """
        item_id = f"item{len(self._items)}"
        self._items.append({"id": item_id, "values": values})
        return item_id

    def selection(self):
        """Returns the current selection.

        :return: List of selected item IDs
        :rtype: list
        """
        return list(self._selection)

    def set_selection(self, ids) -> None:
        """Sets the current selection.

        :param ids: List of item IDs to select
        :return: None
        :rtype: None
        """
        self._selection = list(ids)

    def index(self, item_id: str) -> int:
        """Returns the index of the specified item.

        :param item_id: ID of item to find
        :type item_id: str
        :return: Index of the item
        :rtype: int
        """
        return [item["id"] for item in self._items].index(item_id)


class FakeRepeatVar:
    """Fake StringVar for repeat count testing.

    Simulates a StringVar that holds the repeat count value.
    """

    def __init__(self, value: str) -> None:
        """Initializes the fake repeat variable.

        :param value: Initial repeat count value
        :type value: str
        """
        self._value = value

    def get(self) -> str:
        """Returns the repeat value.

        :return: Current repeat count as string
        :rtype: str
        """
        return self._value


class FakePlayer:
    """Fake player for testing macro playback.

    Tracks play and stop calls without actual playback.
    """

    def __init__(self) -> None:
        """Initializes the fake player.

        Sets up tracking for play and stop calls.
        """
        self.play_calls = []
        self.stop_calls = 0

    def play(self, macro: Macro, repeats: int) -> None:
        """Records a play call.

        :param macro: Macro to play
        :type macro: Macro
        :param repeats: Number of times to repeat
        :type repeats: int
        :return: None
        :rtype: None
        """
        self.play_calls.append((macro, repeats))

    def stop(self) -> None:
        """Records a stop call.

        :return: None
        :rtype: None
        """
        self.stop_calls += 1


class FakeRecorder:
    """Fake recorder for testing macro recording.

    Simulates recording behavior with predefined events.
    """

    def __init__(self, events=None) -> None:
        """Initializes the fake recorder.

        :param events: Predefined events to return on stop
        :type events: list or None
        """
        self.started = False
        self.ignored = None
        self._events = events or []

    def start(self, ignored_hotkeys) -> None:
        """Simulates starting recording.

        :param ignored_hotkeys: Hotkeys to ignore during recording
        :return: None
        :rtype: None
        """
        self.started = True
        self.ignored = ignored_hotkeys

    def stop(self):
        """Simulates stopping recording and returns events.

        :return: List of recorded events
        :rtype: list
        """
        return list(self._events)


def _make_app() -> App:
    """Creates an App instance without initialization.

    Creates a bare App instance using __new__ to bypass __init__,
    allowing tests to set up only the necessary attributes.

    :return: Uninitialized App instance
    :rtype: App
    """
    app = App.__new__(App)
    return app


def test_app_log_writes_text() -> None:
    """Tests that app log writes text to the log widget.

    Verifies that the _log method correctly inserts text into the
    log_text widget with proper newline formatting.

    :return: None
    :rtype: None
    """
    app = _make_app()
    app.log_text = FakeText()

    App._log(app, "hello")

    assert "hello\n" in app.log_text.lines


def test_refresh_hotkey_labels_sets_text() -> None:
    """Tests that hotkey labels are refreshed with correct text.

    Verifies that _refresh_hotkey_labels updates label text to show
    formatted hotkey combinations or "(none)" for empty hotkeys.

    :return: None
    :rtype: None
    """
    app = _make_app()
    app.hotkeys = {"start_record": ["<ctrl>", "r"], "stop_record": []}
    app.hotkey_labels = {"start_record": FakeLabel(), "stop_record": FakeLabel()}

    App._refresh_hotkey_labels(app)

    assert app.hotkey_labels["start_record"].text == "<ctrl>+r"
    assert app.hotkey_labels["stop_record"].text == "(none)"


def test_handle_hotkey_calls_actions() -> None:
    """Tests that hotkey handler calls the correct actions.

    Verifies that _handle_hotkey dispatches to the appropriate app
    methods based on the action name.

    :return: None
    :rtype: None
    """
    app = _make_app()
    called = []
    app.start_recording = lambda: called.append("start_record")
    app.stop_recording = lambda: called.append("stop_record")
    app.start_playback = lambda: called.append("start_macro")
    app.stop_playback = lambda: called.append("stop_macro")
    app.save_macro = lambda: called.append("save_macro")
    app.load_macro = lambda: called.append("load_macro")

    for action in [
        "start_record",
        "stop_record",
        "start_macro",
        "stop_macro",
        "save_macro",
        "load_macro",
    ]:
        App._handle_hotkey(app, action)

    assert called == [
        "start_record",
        "stop_record",
        "start_macro",
        "stop_macro",
        "save_macro",
        "load_macro",
    ]


def test_populate_preview_inserts_rows() -> None:
    """Tests that populate preview inserts rows for macro events.

    Verifies that _populate_preview correctly populates the treeview
    with rows representing each event in the macro.

    :return: None
    :rtype: None
    """
    app = _make_app()
    app.preview = FakeTreeview()
    macro = Macro(
        name="demo",
        events=[
            MacroEvent("key_down", {"key": "a"}, 0),
            MacroEvent("mouse_move", {"x": 1, "y": 2}, 10),
        ],
    )

    App._populate_preview(app, macro)

    assert len(app.preview.get_children()) == 2
    assert app.preview._items[0]["values"][1] == "key_down"


def test_populate_preview_clears_on_none() -> None:
    """Tests that populate preview clears when given None.

    Verifies that _populate_preview removes all items when called with
    None, effectively clearing the preview.

    :return: None
    :rtype: None
    """
    app = _make_app()
    app.preview = FakeTreeview()
    app.preview.insert("", "end", values=(1, "x", "y", 0))

    App._populate_preview(app, None)

    assert app.preview.get_children() == []


def test_can_delete_events_logs_when_empty() -> None:
    """Tests that can_delete_events logs when no macro is loaded.

    Verifies that _can_delete_events returns False and logs an
    appropriate message when current_macro is None.

    :return: None
    :rtype: None
    """
    app = _make_app()
    logs = []
    app._log = logs.append
    app.current_macro = None

    assert App._can_delete_events(app) is False
    assert logs == ["No macro to edit"]


def test_perform_deletion_updates_events() -> None:
    """Tests that perform_deletion correctly removes events.

    Verifies that _perform_deletion removes the specified events from
    the current macro and updates the preview accordingly.

    :return: None
    :rtype: None
    """
    app = _make_app()
    app.preview = FakeTreeview()
    app.current_macro = Macro(
        name="demo",
        events=[
            MacroEvent("key_down", {"key": "a"}, 0),
            MacroEvent("key_up", {"key": "a"}, 0),
            MacroEvent("mouse_move", {"x": 1, "y": 2}, 5),
        ],
    )
    item_ids = [
        app.preview.insert("", "end", values=(1, "key_down", "key=a", 0)),
        app.preview.insert("", "end", values=(2, "key_up", "key=a", 0)),
        app.preview.insert("", "end", values=(3, "mouse_move", "x=1", 5)),
    ]
    deleted = []
    populated = []

    def record_deleted(count: int) -> None:
        """Records deletion count.

        :param count: Number of items deleted
        :type count: int
        :return: None
        :rtype: None
        """
        deleted.append(count)

    def record_populated(macro: Macro | None) -> None:
        """Records populated macro.

        :param macro: Macro that was populated
        :type macro: Macro | None
        :return: None
        :rtype: None
        """
        populated.append(macro)

    app._log_deletion_result = record_deleted
    app._populate_preview = record_populated

    App._perform_deletion(app, [item_ids[0], item_ids[2]])

    assert len(app.current_macro.events) == 1
    assert app.current_macro.events[0].event_type == "key_up"
    assert deleted == [2]
    assert populated[-1] is app.current_macro


def test_start_recording_and_stop_recording() -> None:
    """Tests start and stop recording functionality.

    Verifies that start_recording and stop_recording properly manage
    button states, recorder lifecycle, and macro creation from events.

    :return: None
    :rtype: None
    """
    app = _make_app()
    app.start_rec_btn = FakeButton()
    app.stop_rec_btn = FakeButton()
    app.preview = FakeTreeview()
    app.hotkeys = {"start_record": ["<ctrl>", "r"]}
    app.recorder = FakeRecorder(events=[MacroEvent("key_down", {"key": "a"}, 0)])
    app._populate_preview = lambda macro: setattr(app, "preview_macro", macro)

    App.start_recording(app)
    App.stop_recording(app)

    assert app.start_rec_btn.state == "normal"
    assert app.stop_rec_btn.state == "disabled"
    assert app.recorder.started is True
    assert app.current_macro is not None
    assert app.preview_macro is app.current_macro


def test_start_playback_validation_and_success(monkeypatch) -> None:
    """Tests playback validation and successful playback.

    Verifies that start_playback validates macro existence and repeat
    count before initiating playback, and handles errors appropriately.

    :param monkeypatch: Pytest monkeypatch fixture
    :return: None
    :rtype: None
    """
    app = _make_app()
    warnings = []
    errors = []
    monkeypatch.setattr(app_module, "messagebox", SimpleNamespace(
        showwarning=lambda _t, msg: warnings.append(msg),
        showerror=lambda _t, msg: errors.append(msg),
    ))

    app.current_macro = None
    App.start_playback(app)
    assert warnings == ["No macro loaded"]

    app.current_macro = Macro(name="demo", events=[MacroEvent("key_down", {"key": "a"}, 0)])
    app.repeat_var = FakeRepeatVar("-1")
    App.start_playback(app)
    assert errors[-1] == "Repeat count must be >= 0"

    app.repeat_var = FakeRepeatVar("2")
    app.start_play_btn = FakeButton()
    app.stop_play_btn = FakeButton()
    app.player = FakePlayer()

    App.start_playback(app)

    assert app.start_play_btn.state == "disabled"
    assert app.stop_play_btn.state == "normal"
    assert app.player.play_calls[-1][1] == 2


def test_save_macro_flow(monkeypatch, tmp_path: Path) -> None:
    """Tests the complete save macro flow.

    Verifies that save_macro validates macro existence, prompts for
    file path, updates macro name, and saves to CSV correctly.

    :param monkeypatch: Pytest monkeypatch fixture
    :param tmp_path: Pytest temporary directory fixture
    :type tmp_path: Path
    :return: None
    :rtype: None
    """
    app = _make_app()
    warnings = []
    monkeypatch.setattr(app_module, "messagebox", SimpleNamespace(
        showwarning=lambda _t, msg: warnings.append(msg),
    ))
    app.current_macro = None
    App.save_macro(app)
    assert warnings == ["No macro to save"]

    macro = Macro(name="demo", events=[MacroEvent("key_down", {"key": "a"}, 0)])
    app.current_macro = macro
    logs = []
    app._log = logs.append
    save_calls = []
    target = tmp_path / "demo.csv"
    monkeypatch.setattr(app_module, "filedialog", SimpleNamespace(
        asksaveasfilename=lambda **_kwargs: str(target),
    ))
    monkeypatch.setattr(
        app_module,
        "save_macro_to_csv",
        lambda path, _macro: save_calls.append(path),
    )

    App.save_macro(app)

    assert macro.name == "demo"
    assert save_calls == [target]
    assert "saved" in logs[-1]


def test_load_macro_flow(monkeypatch, tmp_path: Path) -> None:
    """Tests the complete load macro flow.

    Verifies that load_macro prompts for file path, loads from CSV,
    handles empty files, and updates the current macro and preview.

    :param monkeypatch: Pytest monkeypatch fixture
    :param tmp_path: Pytest temporary directory fixture
    :type tmp_path: Path
    :return: None
    :rtype: None
    """
    app = _make_app()
    errors = []
    monkeypatch.setattr(app_module, "messagebox", SimpleNamespace(
        showerror=lambda _t, msg: errors.append(msg),
    ))
    monkeypatch.setattr(app_module, "filedialog", SimpleNamespace(
        askopenfilename=lambda **_kwargs: str(tmp_path / "demo.csv"),
    ))
    monkeypatch.setattr(app_module, "load_macros_from_csv", lambda _path: [])

    App.load_macro(app)
    assert errors == ["No macro found"]

    macro = Macro(name="demo", events=[MacroEvent("key_down", {"key": "a"}, 0)])
    monkeypatch.setattr(app_module, "load_macros_from_csv", lambda _path: [macro])
    logs = []
    app._log = logs.append
    app._populate_preview = lambda _macro: logs.append("preview")

    App.load_macro(app)

    assert app.current_macro is macro
    assert "preview" in logs
    assert "loaded" in logs[-1]
