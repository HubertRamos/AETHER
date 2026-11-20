
import subprocess
from typing import Protocol

from .types import PointerPosition


class PointerBackend(Protocol):
    def move(self, position: PointerPosition) -> None:
        ...


class DryRunPointerBackend:
    """Records pointer movements without controlling the real cursor."""

    def __init__(self) -> None:
        self.positions: list[PointerPosition] = []

    def move(self, position: PointerPosition) -> None:
        if not isinstance(position, PointerPosition):
            raise TypeError("position must be a PointerPosition")

        self.positions.append(position)

    def reset(self) -> None:
        self.positions.clear()


class YdotoolPointerBackend:
    """Controls the real mouse cursor through ydotool."""

    def __init__(self, screen_width: int, screen_height: int) -> None:
        if isinstance(screen_width, bool) or not isinstance(screen_width, int):
            raise TypeError("screen_width must be an integer")

        if isinstance(screen_height, bool) or not isinstance(screen_height, int):
            raise TypeError("screen_height must be an integer")

        if screen_width <= 0 or screen_height <= 0:
            raise ValueError("screen dimensions must be positive")

        self.screen_width = screen_width
        self.screen_height = screen_height

    def move(self, position: PointerPosition) -> None:
        if not isinstance(position, PointerPosition):
            raise TypeError("position must be a PointerPosition")

        x = round(position.x * (self.screen_width - 1))
        y = round(position.y * (self.screen_height - 1))

        subprocess.run(
            [
                "ydotool",
                "mousemove",
                "--absolute",
                "--xpos",
                str(x),
                "--ypos",
                str(y),
            ],
            check=True,
            timeout=2,
        )
