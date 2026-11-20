
from aether.gestures.events import GestureEvent
from aether.gestures.mapping import GestureMapper
from aether.intents.manager import IntentManager

from .dispatcher import ActionDispatcher
from .executor import ActionBackend, ActionExecutor, DryRunBackend
from .types import ActionRequest


class ActionPipeline:
    def __init__(
        self,
        backend: ActionBackend | None = None,
    ):
        self.mapper = GestureMapper()
        self.intent_manager = IntentManager()
        self.dispatcher = ActionDispatcher()

        self.backend = backend if backend is not None else DryRunBackend()
        self.executor = ActionExecutor(self.backend)

    def process(
        self,
        events: list[GestureEvent],
        *,
        enabled: bool,
    ) -> tuple[ActionRequest, ...]:
        if not isinstance(events, list):
            raise TypeError("events deve ser uma lista.")

        if not isinstance(enabled, bool):
            raise TypeError("enabled deve ser bool.")

        if not enabled:
            return self.reset()

        intent_events = self.mapper.map_events(events)

        state_events = self.intent_manager.process_many(intent_events)

        executed = []

        for state_event in state_events:
            request = self.dispatcher.dispatch(
                state_event,
                enabled=True,
            )

            if request is None:
                continue

            results = self.executor.process(
                request,
                enabled=True,
            )

            executed.extend(results)

        return tuple(executed)

    def reset(self) -> tuple[ActionRequest, ...]:
        """Limpa os estados e encerra todas as ações ativas."""
        self.intent_manager.reset()
        self.dispatcher.reset()

        return self.executor.process(
            None,
            enabled=False,
        )
