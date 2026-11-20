
from dataclasses import dataclass
from typing import Protocol

from aether.gestures.events import GestureEventType

from .types import Action, ActionRequest


class ActionBackend(Protocol):
    def execute(self, request: ActionRequest) -> None:
        """Executa ou simula uma solicitação de ação."""
        ...


@dataclass(frozen=True)
class ExecutionRecord:
    hand: str
    action: Action
    event_type: GestureEventType
    previous_action: Action | None = None


class DryRunBackend:
    """Backend que registra solicitações sem controlar o desktop."""

    def __init__(self):
        self.records: list[ExecutionRecord] = []

    def execute(self, request: ActionRequest) -> None:
        self.records.append(
            ExecutionRecord(
                hand=request.hand,
                action=request.action,
                event_type=request.event_type,
                previous_action=request.previous_action,
            )
        )



class ActionExecutor:
    def __init__(self, backend: ActionBackend):
        if not callable(getattr(backend, "execute", None)):
            raise TypeError("backend deve implementar execute().")

        self.backend = backend
        self._active: dict[str, Action] = {}


    def process(
        self,
        request: ActionRequest | None,
        *,
        enabled: bool,
    ) -> tuple[ActionRequest, ...]:
        if not isinstance(enabled, bool):
            raise TypeError("enabled deve ser bool.")

        # Desativar sempre encerra ações contínuas.
        if not enabled:
            return self.deactivate()

        if request is None:
            return ()

        if not isinstance(request, ActionRequest):
            raise TypeError("request deve ser ActionRequest ou None.")

        if not isinstance(request.hand, str) or not request.hand:
            raise ValueError("hand deve ser uma string não vazia.")

        if not isinstance(request.action, Action):
            raise TypeError("action deve ser Action.")

        if not isinstance(request.event_type, GestureEventType):
            raise TypeError("event_type inválido.")

        if (
            request.previous_action is not None
            and not isinstance(request.previous_action, Action)
        ):
            raise TypeError("previous_action deve ser Action ou None.")

        if request.event_type == GestureEventType.GESTURE_STARTED:
            return self._start(request)

        if request.event_type == GestureEventType.GESTURE_CHANGED:
            return self._change(request)

        if request.event_type == GestureEventType.GESTURE_ENDED:
            return self._end(request)

        raise ValueError("Tipo de evento desconhecido.")

    def _execute(self, request: ActionRequest) -> None:
        self.backend.execute(request)

    def _start(
        self,
        request: ActionRequest,
    ) -> tuple[ActionRequest, ...]:
        if request.hand in self._active:
            return ()

        if request.previous_action is not None:
            return ()

        self._active[request.hand] = request.action
        self._execute(request)

        return (request,)

    def _change(
        self,
        request: ActionRequest,
    ) -> tuple[ActionRequest, ...]:
        current = self._active.get(request.hand)

        if current is None:
            return ()

        if request.previous_action != current:
            return ()

        if request.action == current:
            return ()

        self._active[request.hand] = request.action
        self._execute(request)

        return (request,)

    def _end(
        self,
        request: ActionRequest,
    ) -> tuple[ActionRequest, ...]:
        current = self._active.get(request.hand)

        if current != request.action:
            return ()

        del self._active[request.hand]
        self._execute(request)

        return (request,)

    def deactivate(self) -> tuple[ActionRequest, ...]:
        """Encerra todas as ações ainda ativas."""
        released = []

        for hand, action in tuple(self._active.items()):
            request = ActionRequest(
                hand=hand,
                action=action,
                event_type=GestureEventType.GESTURE_ENDED,
            )

            self._execute(request)
            released.append(request)

        self._active.clear()

        return tuple(released)

    def active_actions(self) -> dict[str, Action]:
        return dict(self._active)
