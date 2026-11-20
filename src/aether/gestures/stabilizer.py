
from collections import Counter, deque

from .types import Gesture


class GestureStabilizer:
    def __init__(
        self,
        window_size: int = 5,
        min_votes: int = 4,
        unknown_release_frames: int = 8,
    ):
        if window_size < 1:
            raise ValueError("window_size deve ser positivo.")

        if not 1 <= min_votes <= window_size:
            raise ValueError("min_votes deve estar entre 1 e window_size.")

        if unknown_release_frames < 1:
            raise ValueError(
                "unknown_release_frames deve ser positivo."
            )

        self.samples = deque(maxlen=window_size)
        self.min_votes = min_votes
        self.unknown_release_frames = unknown_release_frames

        self.current = Gesture.UNKNOWN
        self.unknown_count = 0

    def update(self, gesture: Gesture) -> Gesture:
        if not isinstance(gesture, Gesture):
            raise TypeError("gesture precisa ser um Gesture.")

        if gesture == Gesture.UNKNOWN:
            self.unknown_count += 1

            if self.unknown_count >= self.unknown_release_frames:
                self.current = Gesture.UNKNOWN
                self.samples.clear()

            return self.current

        self.unknown_count = 0
        self.samples.append(gesture)

        counts = Counter(self.samples)

# O gesto mais frequente deve vencer.
        candidate, votes = counts.most_common(1)[0]

        # Em caso de empate, não troca o gesto atual.
        if votes >= self.min_votes:
            if votes > counts.get(self.current, 0):
                self.current = candidate

        return self.current

    def reset(self) -> None:
        self.samples.clear()
        self.current = Gesture.UNKNOWN
        self.unknown_count = 0
