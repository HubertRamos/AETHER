
from dataclasses import dataclass
from enum import Enum

from aether.gestures.events import GestureEventType
from aether.gestures.mapping import Intent


class IntentState(Enum):
    IDLE = "idle"
    ACTIVE = "active"


@dataclass(frozen=True)
class IntentStateEvent:
    hand: str
    intent: Intent
    event_type: GestureEventType
    previous_intent: Intent | None = None
