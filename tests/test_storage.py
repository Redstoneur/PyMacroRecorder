"""Macro CSV persistence tests.

This module tests the storage functionality for saving and loading
macros to/from CSV files, including error handling for missing or
invalid files.
"""

from pathlib import Path

from pymacrorecorder.models import Macro, MacroEvent
from pymacrorecorder.storage import load_macros_from_csv, save_macro_to_csv



def test_save_and_load_macro(tmp_path: Path) -> None:
    """Saves then reloads a CSV macro.

    Verifies that a macro can be successfully saved to CSV and then
    loaded back with all events and metadata intact.

    :param tmp_path: Pytest temporary directory fixture
    :type tmp_path: Path
    :return: None
    :rtype: None
    """
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
    """Returns an empty list if the file is missing.

    Verifies that load_macros_from_csv gracefully handles missing
    files by returning an empty list.

    :param tmp_path: Pytest temporary directory fixture
    :type tmp_path: Path
    :return: None
    :rtype: None
    """
    missing = tmp_path / "missing.csv"
    assert not load_macros_from_csv(missing)



def test_load_macro_invalid_payload(tmp_path: Path) -> None:
    """Returns an empty list if the CSV payload is invalid.

    Verifies that load_macros_from_csv handles malformed CSV data
    (e.g., invalid JSON payload) by returning an empty list.

    :param tmp_path: Pytest temporary directory fixture
    :type tmp_path: Path
    :return: None
    :rtype: None
    """
    path = tmp_path / "broken.csv"
    path.write_text(
        "id,event_type,payload,delay_ms\n1,key_down,{,0\n",
        encoding="utf-8",
    )

    assert not load_macros_from_csv(path)
