from math import isfinite

from aether.gestures.types import Gesture


class ClickController:
    """Temporarily emits one click when OPEN_PALM first becomes stable."""

    def __init__(
        self,
        double_click_interval: float = 0.28,
        max_pinch_duration: float = 0.45,
    ) -> None:
        # Keep the existing constructor contract during this diagnostic mode.
        for name, value in (
            ("double_click_interval", double_click_interval),
            ("max_pinch_duration", max_pinch_duration),
        ):
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not isfinite(value)
                or value <= 0
            ):
                raise ValueError(f"{name} must be positive")
        self.double_click_interval = float(double_click_interval)
        self.max_pinch_duration = float(max_pinch_duration)
        self._open_palm_active = False

    def process(
        self,
        gesture: Gesture,
        *,
        now: float,
        hand_visible: bool = True,
        enabled: bool = True,
    ) -> int:
        if not isinstance(gesture, Gesture):
            raise TypeError("gesture must be a Gesture")
        if (
            isinstance(now, bool)
            or not isinstance(now, (int, float))
            or not isfinite(now)
        ):
            raise ValueError("now must be a finite number")
        if not isinstance(hand_visible, bool):
            raise TypeError("hand_visible must be a bool")
        if not isinstance(enabled, bool):
            raise TypeError("enabled must be a bool")
        if not enabled or not hand_visible:
            self.reset()
            return 0

        open_palm_active = gesture == Gesture.OPEN_PALM
        if open_palm_active and not self._open_palm_active:
            self._open_palm_active = True
            return 1

        if not open_palm_active:
            self._open_palm_active = False

        return 0

    def reset(self) -> None:
        self._open_palm_active = False
