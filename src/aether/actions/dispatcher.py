
from aether.gestures.events import GestureEventType
from aether.gestures.mapping import Intent
from aether.intents.types import IntentStateEvent

from .types import Action, ActionRequest


DEFAULT_ACTIONS = {
    Intent.POINT: Action.POINTER,
    Intent.SELECT: Action.SELECT,
    Intent.PAUSE: Action.PAUSE,
    Intent.SECONDARY: Action.SECONDARY,
    Intent.HOLD: Action.HOLD,
}


class ActionDispatcher:
    def __init__(
        self,
        mappings: dict[Intent, Action] | None = None,
    ):
        self.mappings = dict(
            DEFAULT_ACTIONS if mappings is None else mappings
        )

        self._active: dict[str, Action] = {}
        self._validate_mappings()

    def _validate_mappings(self):
        if not isinstance(self.mappings, dict):
            raise TypeError("mappings deve ser um dicionário.")

        for intent, action in self.mappings.items():
            if not isinstance(intent, Intent):
                raise TypeError("Chaves devem ser valores de Intent.")

            if not isinstance(action, Action):
                raise TypeError("Valores devem ser valores de Action.")

    def dispatch(
        self,
        event: IntentStateEvent,
        *,
        enabled: bool,
    ) -> ActionRequest | None:
        if not isinstance(event, IntentStateEvent):
            raise TypeError("event deve ser IntentStateEvent.")

        if not isinstance(enabled, bool):
            raise TypeError("enabled deve ser bool.")

        if not isinstance(event.hand, str) or not event.hand:
            raise ValueError("hand deve ser uma string não vazia.")

        if not enabled:
            self.reset()
            return None

        if event.event_type == GestureEventType.GESTURE_STARTED:
            return self._start(event)

        if event.event_type == GestureEventType.GESTURE_CHANGED:
            return self._change(event)

        if event.event_type == GestureEventType.GESTURE_ENDED:
            return self._end(event)

        raise ValueError("Tipo de evento desconhecido.")

    def _start(
        self,
        event: IntentStateEvent,
    ) -> ActionRequest | None:
        action = self.mappings.get(event.intent)

        if action is None:
            return None

        previous = self._active.get(event.hand)

        if previous == action:
            return None

        self._active[event.hand] = action

        return ActionRequest(
            hand=event.hand,
            action=action,
            event_type=(
                GestureEventType.GESTURE_CHANGED
                if previous is not None
                else GestureEventType.GESTURE_STARTED
            ),
            previous_action=previous,
        )

    def _change(
        self,
        event: IntentStateEvent,
    ) -> ActionRequest | None:
        previous = self._active.get(event.hand)
        action = self.mappings.get(event.intent)

        if previous is None or action is None or previous == action:
            return None

        self._active[event.hand] = action

        return ActionRequest(
            hand=event.hand,
            action=action,
            event_type=GestureEventType.GESTURE_CHANGED,
            previous_action=previous,
        )

    def _end(
        self,
        event: IntentStateEvent,
    ) -> ActionRequest | None:
        current = self._active.get(event.hand)
        action = self.mappings.get(event.intent)

        if current is None or current != action:
            return None

        del self._active[event.hand]

        return ActionRequest(
            hand=event.hand,
            action=current,
            event_type=GestureEventType.GESTURE_ENDED,
        )

    def active_actions(self) -> dict[str, Action]:
        return dict(self._active)

    def reset(self) -> None:
        self._active.clear()

    def set_mapping(
        self,
        intent: Intent,
        action: Action | None,
    ) -> None:
        if not isinstance(intent, Intent):
            raise TypeError("intent deve ser Intent.")

        if action is not None and not isinstance(action, Action):
            raise TypeError("action deve ser Action ou None.")

        if action is None:
            self.mappings.pop(intent, None)
        else:
            self.mappings[intent] = action
