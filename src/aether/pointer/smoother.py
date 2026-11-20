
from math import isfinite

from .types import PointerPosition


class PointerSmoother:
    """Smooths pointer movement using an exponential moving average."""

    def __init__(self, alpha: float = 0.35) -> None:
        if isinstance(alpha, bool) or not isinstance(alpha, (int, float)):
            raise TypeError("alpha must be a number")

        if not isfinite(alpha) or not 0.0 < alpha <= 1.0:
            raise ValueError("alpha must be between 0.0 and 1.0")

        self.alpha = float(alpha)
        self._previous: PointerPosition | None = None

    def process(self, position: PointerPosition) -> PointerPosition:
        if not isinstance(position, PointerPosition):
            raise TypeError("position must be a PointerPosition")

        if self._previous is None:
            self._previous = position
            return position

        x = self._previous.x + self.alpha * (
            position.x - self._previous.x
        )
        y = self._previous.y + self.alpha * (
            position.y - self._previous.y
        )

        smoothed = PointerPosition(x, y)
        self._previous = smoothed

        return smoothed

    def reset(self) -> None:
        self._previous = None
