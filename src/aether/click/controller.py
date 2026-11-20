from math import isfinite

from aether.gestures.types import Gesture


class ClickController:
    """Recognizes quick pinch releases as single or double clicks."""

    def __init__(
        self,
        double_click_interval: float = 0.28,
        max_pinch_duration: float = 0.45,
    ) -> None:
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
        self._pinching = False
        self._press_started_at: float | None = None
        self._pending_click_at: float | None = None
        self._second_press = False

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

        emitted = 0
        if (
            self._pending_click_at is not None
            and not self._second_press
            and now - self._pending_click_at > self.double_click_interval
        ):
            self._pending_click_at = None
            emitted = 1

        pinching = gesture == Gesture.PINCH
        if pinching and not self._pinching:
            self._pinching = True
            self._press_started_at = now
            self._second_press = (
                self._pending_click_at is not None
                and now - self._pending_click_at <= self.double_click_interval
            )
            if not self._second_press:
                self._pending_click_at = None

        elif not pinching and self._pinching:
            duration = now - self._press_started_at
            self._pinching = False
            self._press_started_at = None
            if duration <= self.max_pinch_duration:
                if self._second_press:
                    self._pending_click_at = None
                    self._second_press = False
                    emitted = 2
                else:
                    self._pending_click_at = now
            elif self._second_press:
                self._second_press = False
                self._pending_click_at = None
                emitted = 1
            else:
                self._pending_click_at = None
        return emitted

    def reset(self) -> None:
        self._pinching = False
        self._press_started_at = None
        self._pending_click_at = None
        self._second_press = False
