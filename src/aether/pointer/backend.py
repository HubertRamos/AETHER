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