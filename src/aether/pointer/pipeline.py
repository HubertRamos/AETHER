
from collections.abc import Mapping, Set
from math import isfinite

from aether.gestures.types import Gesture

from .calibration import PointerCalibration
from .controller import PointerController
from .smoother import PointerSmoother
from .types import PointerPosition


class PointerPipeline:
    """Connects stabilized hand gestures to calibrated pointer movement."""

    def __init__(
        self,
        controller: PointerController,
        pointer_hand: str,
        smoothing_alpha: float = 0.35,
        calibration: PointerCalibration | None = None,
        mode: str = "absolute",
        relative_sensitivity: float = 2.0,
    ) -> None:
        if not isinstance(controller, PointerController):
            raise TypeError("controller must be a PointerController")

        if not isinstance(pointer_hand, str) or not pointer_hand.strip():
            raise ValueError("pointer_hand must be a non-empty string")

        if calibration is not None and not isinstance(
            calibration, PointerCalibration
        ):
            raise TypeError("calibration must be a PointerCalibration or None")

        if mode not in ("absolute", "relative"):
            raise ValueError("mode must be 'absolute' or 'relative'")

        if (
            isinstance(relative_sensitivity, bool)
            or not isinstance(relative_sensitivity, (int, float))
        ):
            raise TypeError("relative_sensitivity must be a number")

        if not isfinite(relative_sensitivity) or relative_sensitivity <= 0:
            raise ValueError("relative_sensitivity must be positive and finite")

        self.controller = controller
        self.pointer_hand = pointer_hand
        self.smoother = PointerSmoother(smoothing_alpha)
        self.calibration = calibration or PointerCalibration()
        self.mode = mode
        self.relative_sensitivity = float(relative_sensitivity)

        self._relative_anchor: PointerPosition | None = None

        center_x = (
            self.calibration.screen_left
            + self.calibration.screen_right
        ) / 2

        center_y = (
            self.calibration.screen_top
            + self.calibration.screen_bottom
        ) / 2

        self._last_pointer_position = PointerPosition(center_x, center_y)

    def process(
        self,
        positions: Mapping[str, PointerPosition],
        gestures: Mapping[str, Gesture],
        *,
        enabled: bool,
        suppressed_hands: Set[str] = frozenset(),
    ) -> bool:
        if not isinstance(enabled, bool):
            raise TypeError("enabled must be a bool")

        if not isinstance(positions, Mapping):
            raise TypeError("positions must be a mapping")

        if not isinstance(gestures, Mapping):
            raise TypeError("gestures must be a mapping")

        if not isinstance(suppressed_hands, Set):
            raise TypeError("suppressed_hands must be a set")

        for hand, position in positions.items():
            if not isinstance(hand, str):
                raise TypeError("hand labels must be strings")

            if not isinstance(position, PointerPosition):
                raise TypeError("all positions must be PointerPosition")

        for hand, gesture in gestures.items():
            if not isinstance(hand, str):
                raise TypeError("hand labels must be strings")

            if not isinstance(gesture, Gesture):
                raise TypeError("all gestures must be Gesture")

        if any(not isinstance(hand, str) for hand in suppressed_hands):
            raise TypeError("suppressed hand labels must be strings")

        position = positions.get(self.pointer_hand)
        gesture = gestures.get(self.pointer_hand)

        allowed = (
            enabled
            and position is not None
            and gesture == Gesture.POINT
            and self.pointer_hand not in suppressed_hands
        )

        if not allowed:
            self.smoother.reset()
            self._relative_anchor = None
            return self.controller.process(None, enabled=False)

        smoothed_position = self.smoother.process(position)
        calibrated_position = self.calibration.transform(smoothed_position)

        if self.mode == "absolute":
            target = calibrated_position

        else:
            if self._relative_anchor is None:
                # Start or resume tracking without moving the cursor.
                self._relative_anchor = calibrated_position
                target = self._last_pointer_position

            else:
                delta_x = (
                    calibrated_position.x - self._relative_anchor.x
                ) * self.relative_sensitivity

                delta_y = (
                    calibrated_position.y - self._relative_anchor.y
                ) * self.relative_sensitivity

                target_x = self._last_pointer_position.x + delta_x
                target_y = self._last_pointer_position.y + delta_y

                target = PointerPosition(
                    max(
                        self.calibration.screen_left,
                        min(self.calibration.screen_right, target_x),
                    ),
                    max(
                        self.calibration.screen_top,
                        min(self.calibration.screen_bottom, target_y),
                    ),
                )

            self._relative_anchor = calibrated_position
            self._last_pointer_position = target

        return self.controller.process(target, enabled=True)

    def reset(self) -> None:
        """Reset hand tracking while preserving the current cursor position."""
        self.smoother.reset()
        self._relative_anchor = None
