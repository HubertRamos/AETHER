import subprocess
from typing import Protocol


class ClickBackend(Protocol):
    def click(self, count: int = 1, button: str = "left") -> None:
        """Execute one or more clicks with the requested mouse button."""
        ...


class DryRunClickBackend:
    def __init__(self) -> None:
        self.clicks: list[int] = []
        self.buttons: list[str] = []

    def click(self, count: int = 1, button: str = "left") -> None:
        if isinstance(count, bool) or not isinstance(count, int):
            raise TypeError("count must be an integer")
        if count not in (1, 2):
            raise ValueError("count must be 1 or 2")
        if button not in ("left", "right"):
            raise ValueError("button must be 'left' or 'right'")
        self.clicks.append(count)
        self.buttons.append(button)

    def reset(self) -> None:
        self.clicks.clear()
        self.buttons.clear()


class YdotoolClickBackend:
    BUTTON_CODES = {"left": "0xC0", "right": "0xC1"}

    def click(self, count: int = 1, button: str = "left") -> None:
        if isinstance(count, bool) or not isinstance(count, int):
            raise TypeError("count must be an integer")
        if count not in (1, 2):
            raise ValueError("count must be 1 or 2")
        try:
            code = self.BUTTON_CODES[button]
        except (KeyError, TypeError):
            raise ValueError("button must be 'left' or 'right'") from None
        for _ in range(count):
            subprocess.run(["ydotool", "click", code], check=True, timeout=2)
