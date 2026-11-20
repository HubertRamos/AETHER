from collections.abc import Mapping, Set

from aether.gestures.types import Gesture

from .backend import ClickBackend
from .controller import ClickController


class ClickPipeline:
    """Connects the left-hand pinch gesture to the click backend."""

    def __init__(
        self,
        controller: ClickController,
        backend: ClickBackend,
        click_hand: str = "Left",
    ) -> None:
        if not isinstance(controller, ClickController):
            raise TypeError("controller must be a ClickController")
        if not callable(getattr(backend, "click", None)):
            raise TypeError("backend must implement click()")
        if not isinstance(click_hand, str) or not click_hand.strip():
            raise ValueError("click_hand must be a non-empty string")
        self.controller = controller
        self.backend = backend
        self.click_hand = click_hand

    def process(
        self,
        gestures: Mapping[str, Gesture],
        *,
        now: float,
        enabled: bool,
        suppressed_hands: Set[str] = frozenset(),
    ) -> int:
        if not isinstance(gestures, Mapping):
            raise TypeError("gestures must be a mapping")
        if not isinstance(enabled, bool):
            raise TypeError("enabled must be a bool")
        if not isinstance(suppressed_hands, Set):
            raise TypeError("suppressed_hands must be a set")
        for hand, gesture in gestures.items():
            if not isinstance(hand, str):
                raise TypeError("hand labels must be strings")
            if not isinstance(gesture, Gesture):
                raise TypeError("all gestures must be Gesture")
        if any(not isinstance(hand, str) for hand in suppressed_hands):
            raise TypeError("suppressed hand labels must be strings")

        suppressed = self.click_hand in suppressed_hands
        detected = self.click_hand in gestures

        # A brief camera dropout is treated as a release, not as a reset.
        # This preserves a recognized pinch and lets its click complete.
        # Explicit suppression or deactivation still cancels all pending input.
        if not enabled or suppressed:
            gesture = Gesture.UNKNOWN
            hand_visible = False
        else:
            gesture = gestures.get(self.click_hand, Gesture.UNKNOWN)
            hand_visible = True

        count = self.controller.process(
            gesture,
            now=now,
            hand_visible=hand_visible,
            enabled=enabled,
        )
        if count:
            self.backend.click(count=count)
        return count

    def reset(self) -> None:
        self.controller.reset()
