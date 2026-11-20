import subprocess
from typing import Protocol


class ClickBackend(Protocol):
    def click(self, count: int = 1) -> None:
        """Execute one or more left clicks."""
        ...


class DryRunClickBackend:
    """Records click requests without controlling the desktop."""

    def __init__(self) -> None:
        self.clicks: list[int] = []

    def click(self, count: int = 1) -> None:
        if isinstance(count, bool) or not isinstance(count, int):
            raise TypeError("count must be an integer")
        if count not in (1, 2):
            raise ValueError("count must be 1 or 2")
        self.clicks.append(count)

    def reset(self) -> None:
        self.clicks.clear()


class YdotoolClickBackend:
    """Executes real left clicks through ydotool."""

    def click(self, count: int = 1) -> None:
        if isinstance(count, bool) or not isinstance(count, int):
            raise TypeError("count must be an integer")
        if count not in (1, 2):
            raise ValueError("count must be 1 or 2")
        for _ in range(count):
            subprocess.run(
                ["ydotool", "click", "0xC0"],
                check=True,
                timeout=2,
            )
