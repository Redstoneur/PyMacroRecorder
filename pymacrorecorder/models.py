"""Core models for macro recording and playback."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class MacroEvent:
    event_type: str
    payload: Dict[str, object]
    delay_ms: int


@dataclass
class Macro:
    name: str
    events: List[MacroEvent] = field(default_factory=list)

    def is_empty(self) -> bool:
        return len(self.events) == 0


