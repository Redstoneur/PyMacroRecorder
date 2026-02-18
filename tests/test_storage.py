"""Macro CSV persistence tests."""

from pathlib import Path

from pymacrorecorder.models import Macro, MacroEvent
from pymacrorecorder.storage import load_macros_from_csv, save_macro_to_csv



def test_save_and_load_macro(tmp_path: Path) -> None:
    """Saves then reloads a CSV macro."""
    macro = Macro(
        name="demo",
        events=[
            MacroEvent(event_type="key_down", payload={"key": "a"}, delay_ms=0),
            MacroEvent(event_type="mouse_move", payload={"x": 10, "y": 20}, delay_ms=12),
        ],
    )
    path = tmp_path / "demo.csv"

    save_macro_to_csv(path, macro)
    loaded = load_macros_from_csv(path)

    assert len(loaded) == 1
    assert loaded[0].name == "demo"
    assert len(loaded[0].events) == 2
    assert loaded[0].events[0].payload == {"key": "a"}
    assert loaded[0].events[1].payload == {"x": 10, "y": 20}



def test_load_macro_missing_file(tmp_path: Path) -> None:
    """Returns an empty list if the file is missing."""
    missing = tmp_path / "missing.csv"
    assert not load_macros_from_csv(missing)



def test_load_macro_invalid_payload(tmp_path: Path) -> None:
    """Returns an empty list if the CSV is invalid."""
    path = tmp_path / "broken.csv"
    path.write_text(
        "id,event_type,payload,delay_ms\n1,key_down,{,0\n",
        encoding="utf-8",
    )

    assert not load_macros_from_csv(path)
