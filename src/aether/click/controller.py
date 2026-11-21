from math import isfinite

from aether.gestures.types import Gesture


class ClickController:
    """Converte gestos em cliques simples ou estados de botão pressionado."""

    def __init__(self, double_click_interval: float = 0.28, max_pinch_duration: float = 0.45) -> None:
        for name, value in (("double_click_interval", double_click_interval), ("max_pinch_duration", max_pinch_duration)):
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value) or value <= 0:
                raise ValueError(f"{name} must be positive")
        self.double_click_interval = float(double_click_interval)
        self.max_pinch_duration = float(max_pinch_duration)
        self._active_button: str | None = None
        self._pressed_button: str | None = None
        self._released_button: str | None = None

    @property
    def active_button(self) -> str | None:
        return self._active_button

    @property
    def pressed_button(self) -> str | None:
        return self._pressed_button

    @property
    def released_button(self) -> str | None:
        return self._released_button

    def process(self, gesture: Gesture, *, now: float, hand_visible: bool = True, enabled: bool = True) -> int:
        if not isinstance(gesture, Gesture):
            raise TypeError("gesture must be a Gesture")
        if isinstance(now, bool) or not isinstance(now, (int, float)) or not isfinite(now):
            raise ValueError("now must be a finite number")
        if not isinstance(hand_visible, bool):
            raise TypeError("hand_visible must be a bool")
        if not isinstance(enabled, bool):
            raise TypeError("enabled must be a bool")

        self._released_button = None
        if not enabled or not hand_visible:
            self._release_state()
            return 0

        simple_button = None
        press_button = None
        if gesture in (Gesture.PINCH, Gesture.LEFT_CLICK):
            simple_button = "left"
        elif gesture == Gesture.RIGHT_CLICK:
            simple_button = "right"
        elif gesture == Gesture.LEFT_PRESS:
            press_button = "left"
        elif gesture == Gesture.RIGHT_PRESS:
            press_button = "right"

        if self._pressed_button is not None and press_button != self._pressed_button:
            self._released_button = self._pressed_button
            self._pressed_button = None

        if press_button is not None:
            if self._pressed_button == press_button:
                self._active_button = press_button
                return 0
            self._pressed_button = press_button
            self._active_button = press_button
            return 0

        if simple_button is None:
            self._active_button = None
            return 0

        if simple_button != self._active_button:
            self._active_button = simple_button
            return 1
        return 0

    def _release_state(self) -> None:
        if self._pressed_button is not None:
            self._released_button = self._pressed_button
        self._pressed_button = None
        self._active_button = None

    def reset(self) -> None:
        self._release_state()
