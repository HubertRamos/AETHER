
from aether.gestures.events import GestureEventType
from aether.gestures.mapping import Intent, IntentEvent

from .types import IntentStateEvent


class IntentManager:
    def __init__(self):
        self._active: dict[str, Intent] = {}

    def process(
        self,
        event: IntentEvent,
    ) -> IntentStateEvent | None:
        if not isinstance(event, IntentEvent):
            raise TypeError("event deve ser IntentEvent.")

        if not isinstance(event.hand, str) or not event.hand:
            raise ValueError("hand deve ser uma string não vazia.")

        if event.event_type == GestureEventType.GESTURE_STARTED:
            return self._start(event)

        if event.event_type == GestureEventType.GESTURE_CHANGED:
            return self._change(event)

        if event.event_type == GestureEventType.GESTURE_ENDED:
            return self._end(event)

        raise ValueError("Tipo de evento desconhecido.")

    def _start(
        self,
        event: IntentEvent,
    ) -> IntentStateEvent | None:
        previous = self._active.get(event.hand)

        if previous == event.intent:
            return None

        self._active[event.hand] = event.intent

        if previous is not None:
            return IntentStateEvent(
                hand=event.hand,
                intent=event.intent,
                event_type=GestureEventType.GESTURE_CHANGED,
                previous_intent=previous,
            )

        return IntentStateEvent(
            hand=event.hand,
            intent=event.intent,
            event_type=GestureEventType.GESTURE_STARTED,
        )

    def _change(
        self,
        event: IntentEvent,
    ) -> IntentStateEvent | None:
        previous = self._active.get(event.hand)

        if previous is None or previous == event.intent:
            return None

        self._active[event.hand] = event.intent

        return IntentStateEvent(
            hand=event.hand,
            intent=event.intent,
            event_type=GestureEventType.GESTURE_CHANGED,
            previous_intent=previous,
        )

    def _end(
        self,
        event: IntentEvent,
    ) -> IntentStateEvent | None:
        current = self._active.get(event.hand)

        if current is None or current != event.intent:
            return None

        del self._active[event.hand]

        return IntentStateEvent(
            hand=event.hand,
            intent=current,
            event_type=GestureEventType.GESTURE_ENDED,
        )

    def process_many(
        self,
        events: list[IntentEvent],
    ) -> list[IntentStateEvent]:
        if not isinstance(events, list):
            raise TypeError("events deve ser uma lista.")

        results = []

        for event in events:
            result = self.process(event)

            if result is not None:
                results.append(result)

        return results

    def active_intents(self) -> dict[str, Intent]:
        return dict(self._active)

    def reset(self) -> None:
        self._active.clear()
