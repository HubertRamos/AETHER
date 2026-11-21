import subprocess
from typing import Protocol


class ClickBackend(Protocol):
    def click(self, count: int = 1, button: str = "left") -> None: ...
    def press(self, button: str = "left") -> None: ...
    def release(self, button: str = "left") -> None: ...
    def press_window_drag(self) -> None: ...
    def release_window_drag(self) -> None: ...


class DryRunClickBackend:
    def __init__(self) -> None:
        self.clicks: list[int] = []
        self.buttons: list[str] = []
        self.presses: list[str] = []
        self.releases: list[str] = []
        self.window_drag_starts = 0
        self.window_drag_ends = 0

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

    def press_window_drag(self) -> None:
        self.window_drag_starts += 1

    def release_window_drag(self) -> None:
        self.window_drag_ends += 1

    def reset(self) -> None:
        self.clicks.clear()
        self.buttons.clear()
        self.presses.clear()
        self.releases.clear()


class YdotoolClickBackend:
    BUTTON_CODES = {"left": "0xC0", "right": "0xC1"}
    BUTTON_DOWN_CODES = {"left": "0x40", "right": "0x41"}
    BUTTON_UP_CODES = {"left": "0x80", "right": "0x81"}

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
        try:
            code = self.BUTTON_DOWN_CODES[button]
        except (KeyError, TypeError):
            raise ValueError("button must be 'left' or 'right'") from None
        subprocess.run(["ydotool", "click", code], check=True, timeout=2)

    def release(self, button: str = "left") -> None:
        try:
            code = self.BUTTON_UP_CODES[button]
        except (KeyError, TypeError):
            raise ValueError("button must be 'left' or 'right'") from None
        subprocess.run(["ydotool", "click", code], check=True, timeout=2)

    def press_window_drag(self) -> None:
        # KEY_LEFTMETA (Super) is Linux input keycode 125.
        subprocess.run(["ydotool", "key", "125:1"], check=True, timeout=2)
        try:
            subprocess.run(["ydotool", "click", "0x40"], check=True, timeout=2)
        except Exception:
            subprocess.run(["ydotool", "key", "125:0"], check=True, timeout=2)
            raise

    def release_window_drag(self) -> None:
        # Release the mouse first, then Super, even if mouse release fails.
        try:
            subprocess.run(["ydotool", "click", "0x80"], check=True, timeout=2)
        finally:
            subprocess.run(["ydotool", "key", "125:0"], check=True, timeout=2)
