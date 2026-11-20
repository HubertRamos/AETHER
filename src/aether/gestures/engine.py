from .events import GestureEvent, GestureEventType
from .types import Gesture


class GestureEngine:
    def __init__(self):
        self.active_gestures: dict[str, Gesture] = {}

    def update(
        self,
        hands: dict[str, Gesture],
    ) -> list[GestureEvent]:

        events = []

        for hand, gesture in hands.items():
            if not isinstance(gesture, Gesture):
                raise TypeError(
                    "Todos os gestos devem ser Gesture."
                )

            previous = self.active_gestures.get(hand)

            if gesture == Gesture.UNKNOWN:
                if previous is not None:
                    events.append(
                        GestureEvent(
                            event_type=GestureEventType.GESTURE_ENDED,
                            hand=hand,
                            gesture=previous,
                            previous_gesture=previous,
                        )
                    )
                    del self.active_gestures[hand]

                continue

            if previous is None:
                events.append(
                    GestureEvent(
                        event_type=GestureEventType.GESTURE_STARTED,
                        hand=hand,
                        gesture=gesture,
                    )
                )

            elif previous != gesture:
                events.append(
                    GestureEvent(
                        event_type=GestureEventType.GESTURE_CHANGED,
                        hand=hand,
                        gesture=gesture,
                        previous_gesture=previous,
                    )
                )

            self.active_gestures[hand] = gesture

        # Encerra mãos que desapareceram completamente.
        missing_hands = (
            self.active_gestures.keys() - hands.keys()
        )

        for hand in missing_hands:
            previous = self.active_gestures.pop(hand)

            events.append(
                GestureEvent(
                    event_type=GestureEventType.GESTURE_ENDED,
                    hand=hand,
                    gesture=previous,
                    previous_gesture=previous,
                )
            )

        return events

    def reset(self) -> None:
        self.active_gestures.clear()