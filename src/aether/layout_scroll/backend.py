import subprocess
from typing import Protocol


class LayoutScrollBackend(Protocol):
    def scroll(self, direction: str) -> None: ...


class DryRunLayoutScrollBackend:
    """Records layout-pan commands without controlling the compositor."""

    def __init__(self) -> None:
        self.directions: list[str] = []

    def scroll(self, direction: str) -> None:
        if direction not in ("left", "right"):
            raise ValueError("direction must be 'left' or 'right'")
        self.directions.append(direction)


class UmbrielLayoutScrollBackend:
    """Pans the active Umbriel scrolling layout through its IPC action."""

    def scroll(self, direction: str) -> None:
        if direction not in ("left", "right"):
            raise ValueError("direction must be 'left' or 'right'")
        subprocess.run(
            ["umbriel", "msg", f"layout-scroll-{direction}"],
            check=True,
            timeout=2,
        )
