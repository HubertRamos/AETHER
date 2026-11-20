
from dataclasses import dataclass, field

from .stabilizer import GestureStabilizer
from .types import Gesture


@dataclass
class HandState:
    label: str
    stabilizer: GestureStabilizer = field(
        default_factory=GestureStabilizer
    )
    missing_frames: int = 0
    visible: bool = False

    @property
    def gesture(self) -> Gesture:
        return self.stabilizer.current


class HandTracker:
    def __init__(self, release_after_frames: int = 8):
        if release_after_frames < 1:
            raise ValueError(
                "release_after_frames deve ser positivo."
            )

        self.release_after_frames = release_after_frames
        self.hands: dict[str, HandState] = {}

    def update(
        self,
        detected: dict[str, Gesture],
    ) -> dict[str, Gesture]:

        for label, gesture in detected.items():
            if not isinstance(gesture, Gesture):
                raise TypeError(
                    "Todos os gestos devem ser Gesture."
                )

            if label not in self.hands:
                self.hands[label] = HandState(label=label)

            hand = self.hands[label]
            hand.visible = True
            hand.missing_frames = 0
            hand.stabilizer.update(gesture)

        for label, hand in list(self.hands.items()):
            if label not in detected:
                hand.visible = False
                hand.missing_frames += 1
                hand.stabilizer.update(Gesture.UNKNOWN)

                if hand.missing_frames >= self.release_after_frames:
                    del self.hands[label]

        return {
            label: hand.gesture
            for label, hand in self.hands.items()
        }

    def visible_gestures(self) -> dict[str, Gesture]:
        return {
            label: hand.gesture
            for label, hand in self.hands.items()
            if hand.visible
        }

    def reset(self) -> None:
        self.hands.clear()
