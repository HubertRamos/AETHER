
from collections.abc import Mapping, Set

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
    ) -> None:
        if not isinstance(controller, PointerController):
            raise TypeError("controller must be a PointerController")

        if not isinstance(pointer_hand, str) or not pointer_hand.strip():
            raise ValueError("pointer_hand must be a non-empty string")

        if calibration is not None and not isinstance(
            calibration, PointerCalibration
        ):
            raise TypeError("calibration must be a PointerCalibration or None")

        self.controller = controller
        self.pointer_hand = pointer_hand
        self.smoother = PointerSmoother(smoothing_alpha)
        self.calibration = calibration or PointerCalibration()

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
            return self.controller.process(None, enabled=False)

        smoothed_position = self.smoother.process(position)
        calibrated_position = self.calibration.transform(smoothed_position)

        return self.controller.process(
            calibrated_position,
            enabled=True,
        )

    def reset(self) -> None:
        self.smoother.reset()
