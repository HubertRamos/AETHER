from math import isfinite


class WindowMoveController:
    """Turns horizontal hand travel into rate-limited window moves."""

    def __init__(self, threshold: float = 0.055, cooldown: float = 0.14) -> None:
        if (
            isinstance(threshold, bool)
            or not isinstance(threshold, (int, float))
            or not isfinite(threshold)
            or threshold <= 0
        ):
            raise ValueError("threshold must be a positive finite number")
        if (
            isinstance(cooldown, bool)
            or not isinstance(cooldown, (int, float))
            or not isfinite(cooldown)
            or cooldown < 0
        ):
            raise ValueError("cooldown must be a non-negative finite number")

        self.threshold = float(threshold)
        self.cooldown = float(cooldown)
        self.previous_x: float | None = None
        self.accumulated_x = 0.0
        self.next_allowed_at = 0.0

    def process(self, x: float, now: float) -> str | None:
        if any(
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not isfinite(value)
            for value in (x, now)
        ):
            raise ValueError("x and now must be finite numbers")

        x = float(x)
        now = float(now)

        if self.previous_x is None:
            self.previous_x = x
            return None

        self.accumulated_x += x - self.previous_x
        self.previous_x = x

        if abs(self.accumulated_x) < self.threshold:
            return None

        if now < self.next_allowed_at:
            self.accumulated_x = max(
                -self.threshold,
                min(self.threshold, self.accumulated_x),
            )
            return None

        direction = "right" if self.accumulated_x > 0 else "left"
        self.accumulated_x = 0.0
        self.next_allowed_at = now + self.cooldown
        return direction

    def reset(self) -> None:
        self.previous_x = None
        self.accumulated_x = 0.0
        self.next_allowed_at = 0.0
