"""CSV persistence for macros and hotkeys."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import List

from .models import Macro, MacroEvent

CSV_FIELDS = ["id", "event_type", "payload", "delay_ms"]


def save_macro_to_csv(path: Path, macro: Macro) -> None:
    """Write a macro to CSV with one event per line.

    The macro name is derived from the filename (without extension).

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
        for idx, event in enumerate(macro.events, start=1):
            writer.writerow({
                "id": idx,
                "event_type": event.event_type,
                "payload": json.dumps(event.payload),
                "delay_ms": event.delay_ms,
            })


def load_macros_from_csv(path: Path) -> List[Macro]:
    """Load a macro from a CSV file.

    The macro name is derived from the filename (without extension).

    :param path: Source CSV path.
    :type path: pathlib.Path
    :return: Parsed macro as a single-item list, or empty list if file not found.
    :rtype: list[Macro]
    """
    macros: List[Macro] = []
    if not path.exists():
        return macros
    try:
        macro_name = path.stem
        events: List[MacroEvent] = []
        with path.open("r", newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                raw_payload = json.loads(row.get("payload", "{}"))
                event = MacroEvent(
                    event_type=row.get("event_type", ""),
                    payload=raw_payload,
                    delay_ms=int(row.get("delay_ms", 0)),
                )
                events.append(event)
        macros.append(Macro(name=macro_name, events=events))
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return []
    return macros
