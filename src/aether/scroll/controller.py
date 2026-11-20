from math import hypot, isfinite


class ScrollController:
    """Converts hand movement into velocity-based scroll events."""

    def __init__(
        self,
        sensitivity: float = 1800.0,
        deadzone: float = 0.015,
        max_speed: float = 3.0,
        smoothing: float = 0.35,
    ) -> None:
        values = (sensitivity, deadzone, max_speed, smoothing)

        if any(
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not isfinite(value)
            for value in values
        ):
            raise ValueError("Controller parameters must be finite numbers")

        if sensitivity <= 0 or deadzone < 0 or max_speed <= 0:
            raise ValueError("Invalid sensitivity, deadzone or max_speed")

        if not 0 < smoothing <= 1:
            raise ValueError("smoothing must be between 0 and 1")

        self.sensitivity = float(sensitivity)
        self.deadzone = float(deadzone)
        self.max_speed = float(max_speed)
        self.smoothing = float(smoothing)

        self.previous_position = None
        self.filtered_x = 0.0
        self.filtered_y = 0.0
        self.accumulator_x = 0.0
        self.accumulator_y = 0.0

    def process(self, x: float, y: float, elapsed: float) -> tuple[int, int]:
        values = (x, y, elapsed)

        if any(
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not isfinite(value)
            for value in values
        ):
            raise ValueError("Position and elapsed must be finite numbers")

        if not 0 < elapsed <= 0.25:
            self.reset()
            return 0, 0

        position = (float(x), float(y))

        if self.previous_position is None:
            self.previous_position = position
            return 0, 0

        dx = position[0] - self.previous_position[0]
        dy = position[1] - self.previous_position[1]
        self.previous_position = position

        distance = hypot(dx, dy)

        if distance < self.deadzone * elapsed:
            dx = 0.0
            dy = 0.0

        velocity_x = dx / elapsed
        velocity_y = dy / elapsed

        self.filtered_x += self.smoothing * (
            velocity_x - self.filtered_x
        )
        self.filtered_y += self.smoothing * (
            velocity_y - self.filtered_y
        )

        self.filtered_x = max(
            -self.max_speed,
            min(self.max_speed, self.filtered_x),
        )
        self.filtered_y = max(
            -self.max_speed,
            min(self.max_speed, self.filtered_y),
        )

        self.accumulator_x += (
            self.filtered_x * self.sensitivity * elapsed
        )
        self.accumulator_y += (
            self.filtered_y * self.sensitivity * elapsed
        )

        horizontal = int(self.accumulator_x)
        vertical = int(self.accumulator_y)

        self.accumulator_x -= horizontal
        self.accumulator_y -= vertical

        return vertical, horizontal

    def reset(self) -> None:
        self.previous_position = None
        self.filtered_x = 0.0
        self.filtered_y = 0.0
        self.accumulator_x = 0.0
        self.accumulator_y = 0.0