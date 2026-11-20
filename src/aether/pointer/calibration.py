
from dataclasses import dataclass
from math import isfinite

from .types import PointerPosition


@dataclass(frozen=True)
class PointerCalibration:
    """Maps a camera region to a normalized screen region."""

    camera_left: float = 0.0
    camera_top: float = 0.0
    camera_right: float = 1.0
    camera_bottom: float = 1.0

    screen_left: float = 0.0
    screen_top: float = 0.0
    screen_right: float = 1.0
    screen_bottom: float = 1.0

    invert_x: bool = False
    invert_y: bool = False

    def __post_init__(self) -> None:
        coordinates = (
            "camera_left",
            "camera_top",
            "camera_right",
            "camera_bottom",
            "screen_left",
            "screen_top",
            "screen_right",
            "screen_bottom",
        )

        for name in coordinates:
            value = getattr(self, name)

            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeError(f"{name} must be a number")

            if not isfinite(value) or not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0.0 and 1.0")

        if self.camera_left >= self.camera_right:
            raise ValueError("camera_left must be less than camera_right")

        if self.camera_top >= self.camera_bottom:
            raise ValueError("camera_top must be less than camera_bottom")

        if self.screen_left >= self.screen_right:
            raise ValueError("screen_left must be less than screen_right")

        if self.screen_top >= self.screen_bottom:
            raise ValueError("screen_top must be less than screen_bottom")

        if not isinstance(self.invert_x, bool):
            raise TypeError("invert_x must be a bool")

        if not isinstance(self.invert_y, bool):
            raise TypeError("invert_y must be a bool")

    def transform(self, position: PointerPosition) -> PointerPosition:
        if not isinstance(position, PointerPosition):
            raise TypeError("position must be a PointerPosition")

        x_ratio = (
            (position.x - self.camera_left)
            / (self.camera_right - self.camera_left)
        )

        y_ratio = (
            (position.y - self.camera_top)
            / (self.camera_bottom - self.camera_top)
        )

        x_ratio = max(0.0, min(1.0, x_ratio))
        y_ratio = max(0.0, min(1.0, y_ratio))

        if self.invert_x:
            x_ratio = 1.0 - x_ratio

        if self.invert_y:
            y_ratio = 1.0 - y_ratio

        screen_x = (
            self.screen_left
            + x_ratio * (self.screen_right - self.screen_left)
        )

        screen_y = (
            self.screen_top
            + y_ratio * (self.screen_bottom - self.screen_top)
        )

        return PointerPosition(screen_x, screen_y)
