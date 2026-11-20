from dataclasses import dataclass
from enum import Enum

from .types import Gesture


class GestureEventType(Enum):
    GESTURE_STARTED = "gesture_started"
    GESTURE_CHANGED = "gesture_changed"
    GESTURE_ENDED = "gesture_ended"


@dataclass(frozen=True)
class GestureEvent:
    event_type: GestureEventType
    hand: str
    gesture: Gesture
    previous_gesture: Gesture | None = None