
from collections.abc import Mapping, Set

from aether.gestures.types import Gesture
from aether.pointer.types import PointerPosition

from .controller import ScrollController


class ScrollPipeline:
    """Connects stabilized hand gestures to velocity-based scrolling."""

    def __init__(
        self,
        controller: ScrollController,
        backend,
        scroll_hand: str = "Right",
    ) -> None:
        if not isinstance(controller, ScrollController):
            raise TypeError("controller must be a ScrollController")

        if not callable(getattr(backend, "scroll", None)):
            raise TypeError("backend must implement scroll()")

        if not isinstance(scroll_hand, str) or not scroll_hand.strip():
            raise ValueError("scroll_hand must be a non-empty string")

        self.controller = controller
        self.backend = backend
        self.scroll_hand = scroll_hand

    def process(
        self,
        positions: Mapping[str, PointerPosition],
        gestures: Mapping[str, Gesture],
        elapsed: float,
        *,
        enabled: bool,
        suppressed_hands: Set[str] = frozenset(),
    ) -> tuple[int, int]:
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

        position = positions.get(self.scroll_hand)
        gesture = gestures.get(self.scroll_hand)

        allowed = (
            enabled
            and position is not None
            and gesture == Gesture.TWO_FINGERS
            and self.scroll_hand not in suppressed_hands
        )

        if not allowed:
            self.reset()
            return 0, 0

        vertical, horizontal = self.controller.process(
            position.x,
            position.y,
            elapsed,
        )

        if vertical or horizontal:
            self.backend.scroll(
                vertical=vertical,
                horizontal=horizontal,
            )

        return vertical, horizontal

    def reset(self) -> None:
        """Reset tracking and accumulated scroll movement."""
        self.controller.reset()
