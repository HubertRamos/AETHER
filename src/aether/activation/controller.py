import math

from .states import ActivationState


class ActivationController:
    def __init__(
        self,
        arming_timeout: float = 5.0,
        cooldown_duration: float = 1.5,
    ):
        if not math.isfinite(arming_timeout) or arming_timeout <= 0:
            raise ValueError("arming_timeout deve ser positivo.")

        if not math.isfinite(cooldown_duration) or cooldown_duration <= 0:
            raise ValueError("cooldown_duration deve ser positivo.")

        self.arming_timeout = arming_timeout
        self.cooldown_duration = cooldown_duration

        self.state = ActivationState.DISABLED
        self.remaining_time = 0.0

    @property
    def can_execute(self) -> bool:
        return self.state == ActivationState.ACTIVE

    def request_activation(self) -> bool:
        if self.state != ActivationState.DISABLED:
            return False

        self.state = ActivationState.ARMING
        self.remaining_time = self.arming_timeout

        return True

    def confirm_activation(self) -> bool:
        if self.state != ActivationState.ARMING:
            return False

        self.state = ActivationState.ACTIVE
        self.remaining_time = 0.0

        return True

    def cancel_activation(self) -> None:
        if self.state == ActivationState.ARMING:
            self.state = ActivationState.DISABLED
            self.remaining_time = 0.0

    def deactivate(self) -> None:
        if self.state == ActivationState.ACTIVE:
            self._enter_cooldown()

        elif self.state == ActivationState.ARMING:
            self.state = ActivationState.DISABLED
            self.remaining_time = 0.0

    def emergency_stop(self) -> None:
        if self.state != ActivationState.DISABLED:
            self._enter_cooldown()

    def tracking_lost(self) -> None:
        if self.state == ActivationState.ACTIVE:
            self._enter_cooldown()

        elif self.state == ActivationState.ARMING:
            self.state = ActivationState.DISABLED
            self.remaining_time = 0.0

    def update(self, elapsed_seconds: float) -> None:
        if not math.isfinite(elapsed_seconds) or elapsed_seconds < 0:
            raise ValueError("elapsed_seconds deve ser finito e não negativo.")

        if self.state not in (
            ActivationState.ARMING,
            ActivationState.COOLDOWN,
        ):
            return

        self.remaining_time -= elapsed_seconds

        if self.remaining_time > 0:
            return

        self.remaining_time = 0.0
        self.state = ActivationState.DISABLED

    def _enter_cooldown(self) -> None:
        self.state = ActivationState.COOLDOWN
        self.remaining_time = self.cooldown_duration