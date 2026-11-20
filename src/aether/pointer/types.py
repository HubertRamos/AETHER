from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class PointerPosition:
    """Normalized pointer position in camera coordinates."""

    x: float
    y: float

    def __post_init__(self) -> None:
        for name, value in (("x", self.x), ("y", self.y)):
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeError(f"{name} must be a number")

            if not isfinite(value):
                raise ValueError(f"{name} must be finite")

            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0.0 and 1.0")
