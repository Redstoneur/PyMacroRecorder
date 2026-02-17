"""Core models for macro recording and playback."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class MacroEvent:
    """Represents a single keyboard or mouse event within a macro sequence.

    :ivar event_type: Event identifier such as ``key_down`` or ``mouse_click``.
    :vartype event_type: str
    :ivar payload: Event-specific payload values.
    :vartype payload: dict[str, object]
    :ivar delay_ms: Delay before the event in milliseconds.
    :vartype delay_ms: int
    """

    event_type: str
    payload: Dict[str, object]
    delay_ms: int


@dataclass
class Macro:
    """A named collection of macro events.

    :ivar name: Macro display name.
    :vartype name: str
    :ivar events: Ordered list of recorded events.
    :vartype events: list[MacroEvent]
    """

    name: str
    events: List[MacroEvent] = field(default_factory=list)

    def is_empty(self) -> bool:
        """Return whether the macro has no events.

        :return: ``True`` if no events are stored.
        :rtype: bool
        """

        return len(self.events) == 0

