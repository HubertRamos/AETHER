
from dataclasses import dataclass
from enum import Enum

from aether.gestures.events import GestureEventType
from aether.gestures.mapping import Intent


class Action(Enum):
    POINTER = "pointer"
    SELECT = "select"
    PAUSE = "pause"
    SECONDARY = "secondary"
    HOLD = "hold"


@dataclass(frozen=True)
class ActionRequest:
    hand: str
    action: Action
    event_type: GestureEventType
    previous_action: Action | None = None
