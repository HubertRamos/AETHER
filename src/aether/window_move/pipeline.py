from collections.abc import Mapping, Set

from aether.gestures.types import Gesture
from aether.pointer.types import PointerPosition

from .controller import WindowMoveController


class WindowMovePipeline:
    """Maps the right-hand three-finger gesture to focused-window movement."""

    def __init__(
        self,
        controller: WindowMoveController,
        backend,
        move_hand: str = "Right",
    ) -> None:
        if not isinstance(controller, WindowMoveController):
            raise TypeError("controller must be a WindowMoveController")
        if not callable(getattr(backend, "move_focused_window", None)):
            raise TypeError("backend must implement move_focused_window()")
        if not isinstance(move_hand, str) or not move_hand.strip():
            raise ValueError("move_hand must be a non-empty string")

        self.controller = controller
        self.backend = backend
        self.move_hand = move_hand

    def process(
        self,
        positions: Mapping[str, PointerPosition],
        gestures: Mapping[str, Gesture],
        *,
        now: float,
        enabled: bool,
        suppressed_hands: Set[str] = frozenset(),
    ) -> str | None:
        if not isinstance(positions, Mapping):
            raise TypeError("positions must be a mapping")
        if not isinstance(gestures, Mapping):
            raise TypeError("gestures must be a mapping")
        if not isinstance(enabled, bool):
            raise TypeError("enabled must be a bool")
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

        position = positions.get(self.move_hand)
        gesture = gestures.get(self.move_hand)
        allowed = (
            enabled
            and position is not None
            and gesture == Gesture.THREE_FINGER_PAN
            and self.move_hand not in suppressed_hands
        )

        if not allowed:
            self.reset()
            return None

        direction = self.controller.process(position.x, now)
        if direction is not None:
            self.backend.move_focused_window(direction)
        return direction

    def reset(self) -> None:
        self.controller.reset()
