"""Tests headless pour les utilitaires de l'app Tkinter."""

# pylint: disable=missing-class-docstring,missing-function-docstring,too-few-public-methods,protected-access

from pathlib import Path
from types import SimpleNamespace

import pymacrorecorder.app as app_module
from pymacrorecorder.app import App
from pymacrorecorder.models import Macro, MacroEvent


class FakeText:
    def __init__(self) -> None:
        self.state = None
        self.lines = []

    def configure(self, **kwargs) -> None:
        self.state = kwargs.get("state", self.state)

    def insert(self, _where: str, text: str) -> None:
        self.lines.append(text)

    def see(self, _where: str) -> None:
        return None


class FakeLabel:
    def __init__(self) -> None:
        self.text = ""

    def configure(self, **kwargs) -> None:
        self.text = kwargs.get("text", self.text)


class FakeButton:
    def __init__(self) -> None:
        self.state = None

    def configure(self, **kwargs) -> None:
        self.state = kwargs.get("state", self.state)


class FakeTreeview:
    def __init__(self) -> None:
        self._items = []
        self._selection = []

    def get_children(self):
        return [item["id"] for item in self._items]

    def delete(self, item_id: str) -> None:
        self._items = [item for item in self._items if item["id"] != item_id]

    def insert(self, _parent: str, _index: str, values):
        item_id = f"item{len(self._items)}"
        self._items.append({"id": item_id, "values": values})
        return item_id

    def selection(self):
        return list(self._selection)

    def set_selection(self, ids) -> None:
        self._selection = list(ids)

    def index(self, item_id: str) -> int:
        return [item["id"] for item in self._items].index(item_id)


class FakeRepeatVar:
    def __init__(self, value: str) -> None:
        self._value = value

    def get(self) -> str:
        return self._value


class FakePlayer:
    def __init__(self) -> None:
        self.play_calls = []
        self.stop_calls = 0

    def play(self, macro: Macro, repeats: int) -> None:
        self.play_calls.append((macro, repeats))

    def stop(self) -> None:
        self.stop_calls += 1


class FakeRecorder:
    def __init__(self, events=None) -> None:
        self.started = False
        self.ignored = None
        self._events = events or []

    def start(self, ignored_hotkeys) -> None:
        self.started = True
        self.ignored = ignored_hotkeys

    def stop(self):
        return list(self._events)


def _make_app() -> App:
    app = App.__new__(App)
    return app


def test_app_log_writes_text() -> None:
    app = _make_app()
    app.log_text = FakeText()

    App._log(app, "hello")

    assert "hello\n" in app.log_text.lines


def test_refresh_hotkey_labels_sets_text() -> None:
    app = _make_app()
    app.hotkeys = {"start_record": ["<ctrl>", "r"], "stop_record": []}
    app.hotkey_labels = {"start_record": FakeLabel(), "stop_record": FakeLabel()}

    App._refresh_hotkey_labels(app)

    assert app.hotkey_labels["start_record"].text == "<ctrl>+r"
    assert app.hotkey_labels["stop_record"].text == "(none)"


def test_handle_hotkey_calls_actions() -> None:
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
    app = _make_app()
    app.preview = FakeTreeview()
    app.preview.insert("", "end", values=(1, "x", "y", 0))

    App._populate_preview(app, None)

    assert app.preview.get_children() == []


def test_can_delete_events_logs_when_empty() -> None:
    app = _make_app()
    logs = []
    app._log = logs.append
    app.current_macro = None

    assert App._can_delete_events(app) is False
    assert logs == ["No macro to edit"]


def test_perform_deletion_updates_events() -> None:
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
        deleted.append(count)

    def record_populated(macro: Macro | None) -> None:
        populated.append(macro)

    app._log_deletion_result = record_deleted
    app._populate_preview = record_populated

    App._perform_deletion(app, [item_ids[0], item_ids[2]])

    assert len(app.current_macro.events) == 1
    assert app.current_macro.events[0].event_type == "key_up"
    assert deleted == [2]
    assert populated[-1] is app.current_macro


def test_start_recording_and_stop_recording() -> None:
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
