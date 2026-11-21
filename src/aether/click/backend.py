import subprocess
from typing import Protocol


class ClickBackend(Protocol):
    def click(self, count: int = 1, button: str = "left") -> None: ...
    def press(self, button: str = "left") -> None: ...
    def release(self, button: str = "left") -> None: ...


class DryRunClickBackend:
    def __init__(self) -> None:
        self.clicks: list[int] = []
        self.buttons: list[str] = []
        self.presses: list[str] = []
        self.releases: list[str] = []

    def click(self, count: int = 1, button: str = "left") -> None:
        if isinstance(count, bool) or not isinstance(count, int):
            raise TypeError("count must be an integer")
        if count not in (1, 2):
            raise ValueError("count must be 1 or 2")
        if button not in ("left", "right"):
            raise ValueError("button must be 'left' or 'right'")
        self.clicks.append(count)
        self.buttons.append(button)

    def press(self, button: str = "left") -> None:
        if button not in ("left", "right"):
            raise ValueError("button must be 'left' or 'right'")
        self.presses.append(button)

    def release(self, button: str = "left") -> None:
        if button not in ("left", "right"):
            raise ValueError("button must be 'left' or 'right'")
        self.releases.append(button)

    def reset(self) -> None:
        self.clicks.clear()
        self.buttons.clear()
        self.presses.clear()
        self.releases.clear()


class YdotoolClickBackend:
    BUTTON_CODES = {"left": "0xC0", "right": "0xC1"}

    def _code(self, button: str) -> str:
        try:
            return self.BUTTON_CODES[button]
        except (KeyError, TypeError):
            raise ValueError("button must be 'left' or 'right'") from None

    def click(self, count: int = 1, button: str = "left") -> None:
        if isinstance(count, bool) or not isinstance(count, int):
            raise TypeError("count must be an integer")
        if count not in (1, 2):
            raise ValueError("count must be 1 or 2")
        code = self._code(button)
        for _ in range(count):
            subprocess.run(["ydotool", "click", code], check=True, timeout=2)

    def press(self, button: str = "left") -> None:
        subprocess.run(["ydotool", "mousedown", self._code(button)], check=True, timeout=2)

    def release(self, button: str = "left") -> None:
        subprocess.run(["ydotool", "mouseup", self._code(button)], check=True, timeout=2)
