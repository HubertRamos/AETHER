
from dataclasses import dataclass
from enum import Enum

from .events import GestureEvent, GestureEventType
from .types import Gesture


class Intent(Enum):
    POINT = "point"
    SELECT = "select"
    PAUSE = "pause"
    SECONDARY = "secondary"
    HOLD = "hold"


DEFAULT_MAPPINGS = {
    Gesture.POINT: Intent.POINT,
    Gesture.PINCH: Intent.SELECT,
    Gesture.OPEN_PALM: Intent.PAUSE,
    Gesture.TWO_FINGERS: Intent.SECONDARY,
    Gesture.FIST: Intent.HOLD,
}


@dataclass(frozen=True)
class IntentEvent:
    intent: Intent
    hand: str
    event_type: GestureEventType


class GestureMapper:
    def __init__(
        self,
        mappings: dict[Gesture, Intent] | None = None,
    ):
        self.mappings = dict(
            DEFAULT_MAPPINGS if mappings is None else mappings
        )

        self._validate_mappings(self.mappings)

    @staticmethod
    def _validate_mappings(
        mappings: dict[Gesture, Intent],
    ) -> None:
        if not isinstance(mappings, dict):
            raise TypeError("mappings deve ser um dicionário.")

        for gesture, intent in mappings.items():
            if not isinstance(gesture, Gesture):
                raise TypeError(
                    "As chaves devem ser valores de Gesture."
                )

            if not isinstance(intent, Intent):
                raise TypeError(
                    "Os valores devem ser valores de Intent."
                )

    def map_event(
        self,
        event: GestureEvent,
    ) -> IntentEvent | None:
        if not isinstance(event, GestureEvent):
            raise TypeError("event deve ser GestureEvent.")

        intent = self.mappings.get(event.gesture)

        if intent is None:
            return None

        return IntentEvent(
            intent=intent,
            hand=event.hand,
            event_type=event.event_type,
        )

    def map_events(
        self,
        events: list[GestureEvent],
    ) -> list[IntentEvent]:
        if not isinstance(events, list):
            raise TypeError("events deve ser uma lista.")

        mapped = []

        for event in events:
            intent_event = self.map_event(event)

            if intent_event is not None:
                mapped.append(intent_event)

        return mapped

    def set_mapping(
        self,
        gesture: Gesture,
        intent: Intent | None,
    ) -> None:
        if not isinstance(gesture, Gesture):
            raise TypeError("gesture deve ser Gesture.")

        if intent is not None and not isinstance(intent, Intent):
            raise TypeError("intent deve ser Intent ou None.")

        if intent is None:
            self.mappings.pop(gesture, None)
        else:
            self.mappings[gesture] = intent

    def reset_defaults(self) -> None:
        self.mappings = dict(DEFAULT_MAPPINGS)
