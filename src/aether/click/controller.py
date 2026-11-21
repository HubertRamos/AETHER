from math import isfinite

from aether.gestures.types import Gesture


class ClickController:
    """Emits one mouse click on the rising edge of a click gesture."""

    def __init__(self, double_click_interval: float = 0.28, max_pinch_duration: float = 0.45) -> None:
        for name, value in (("double_click_interval", double_click_interval), ("max_pinch_duration", max_pinch_duration)):
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value) or value <= 0:
                raise ValueError(f"{name} must be positive")
        self.double_click_interval = float(double_click_interval)
        self.max_pinch_duration = float(max_pinch_duration)
        self._active_button: str | None = None

    @property
    def active_button(self) -> str | None:
        return self._active_button

    def process(self, gesture: Gesture, *, now: float, hand_visible: bool = True, enabled: bool = True) -> int:
        if not isinstance(gesture, Gesture):
            raise TypeError("gesture must be a Gesture")
        if isinstance(now, bool) or not isinstance(now, (int, float)) or not isfinite(now):
            raise ValueError("now must be a finite number")
        if not isinstance(hand_visible, bool):
            raise TypeError("hand_visible must be a bool")
        if not isinstance(enabled, bool):
            raise TypeError("enabled must be a bool")
        if not enabled or not hand_visible:
            self.reset()
            return 0

        button = None
        if gesture in (Gesture.PINCH, Gesture.LEFT_CLICK):
            button = "left"
        elif gesture == Gesture.RIGHT_CLICK:
            button = "right"

        if button is None:
            self._active_button = None
            return 0
        if button != self._active_button:
            self._active_button = button
            return 1
        return 0

    def reset(self) -> None:
        self._active_button = None
