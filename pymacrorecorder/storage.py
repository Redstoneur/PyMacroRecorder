"""CSV persistence for macros and hotkeys."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import List

from .models import Macro, MacroEvent

CSV_FIELDS = ["name", "events"]


def save_macro_to_csv(path: Path, macro: Macro) -> None:
    """Write a macro to CSV with JSON-encoded events.

    :param path: Destination CSV path.
    :type path: pathlib.Path
    :param macro: Macro to serialize.
    :type macro: Macro
    :return: Nothing.
    :rtype: None
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerow({
            "name": macro.name,
            "events": json.dumps([event.__dict__ for event in macro.events]),
        })


def load_macros_from_csv(path: Path) -> List[Macro]:
    """Load macros from a CSV file.

    :param path: Source CSV path.
    :type path: pathlib.Path
    :return: Parsed macros in file order.
    :rtype: list[Macro]
    """
    macros: List[Macro] = []
    if not path.exists():
        return macros
    try:
        with path.open("r", newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                raw_events = json.loads(row.get("events", "[]"))
                events = [MacroEvent(**evt) for evt in raw_events]
                macros.append(Macro(name=row.get("name", "macro"), events=events))
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return []
    return macros

