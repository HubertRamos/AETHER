
from collections.abc import Mapping

from aether.gestures.types import Gesture

from .controller import ActivationController
from .states import ActivationState


class ActivationCoordinator:
    def __init__(
        self,
        controller: ActivationController | None = None,
    ):
        self.controller = controller or ActivationController()
        self._arming_hand: str | None = None
        self._arming_released = False

    def request_activation(self) -> bool:
        requested = self.controller.request_activation()

        if requested:
            self._arming_hand = None
            self._arming_released = False

        return requested

    def deactivate(self) -> None:
        self.controller.deactivate()
        self._reset_arming()

    def emergency_stop(self) -> None:
        self.controller.emergency_stop()
        self._reset_arming()

    def update(
        self,
        visible_gestures: Mapping[str, Gesture],
        elapsed_seconds: float,
    ) -> bool:
        for gesture in visible_gestures.values():
            if not isinstance(gesture, Gesture):
                raise TypeError(
                    "Todos os gestos devem ser Gesture."
                )

        self.controller.update(elapsed_seconds)

        if self.controller.state != ActivationState.ARMING:
            self._reset_arming()

        if (
            self.controller.state == ActivationState.ACTIVE
            and not visible_gestures
        ):
            self.controller.tracking_lost()
            return False

        if self.controller.state != ActivationState.ARMING:
            return False

        # Seleciona a primeira mão visível da sequência.
        if self._arming_hand is None:
            if not visible_gestures:
                return False

            self._arming_hand = next(iter(visible_gestures))

        # A mão responsável desapareceu: cancela por segurança.
        if self._arming_hand not in visible_gestures:
            self.controller.cancel_activation()
            self._reset_arming()
            return False

        gesture = visible_gestures[self._arming_hand]

        # A mesma mão precisa sair da palma aberta.
        if gesture != Gesture.OPEN_PALM:
            self._arming_released = True
            return False

        # A mesma mão voltou à palma aberta: confirma.
        if self._arming_released:
            confirmed = self.controller.confirm_activation()
            self._reset_arming()
            return confirmed

        return False

    def _reset_arming(self) -> None:
        self._arming_hand = None
        self._arming_released = False

    @property
    def can_execute(self) -> bool:
        return self.controller.can_execute

    @property
    def state(self) -> ActivationState:
        return self.controller.state
