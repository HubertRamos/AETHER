import subprocess
from typing import Protocol


class WindowMoveBackend(Protocol):
    def move_focused_window(self, direction: str) -> None: ...


class DryRunWindowMoveBackend:
    """Records focused-window movement without controlling the compositor."""

    def __init__(self) -> None:
        self.directions: list[str] = []

    def move_focused_window(self, direction: str) -> None:
        if direction not in ("left", "right"):
            raise ValueError("direction must be 'left' or 'right'")
        self.directions.append(direction)


class UmbrielWindowMoveBackend:
    """Moves focus to the neighboring Umbriel window."""

    def move_focused_window(self, direction: str) -> None:
        if direction not in ("left", "right"):
            raise ValueError("direction must be 'left' or 'right'")
        subprocess.run(
            ["umbriel", "msg", f"window-focus-{direction}"],
            check=True,
            timeout=2,
        )
