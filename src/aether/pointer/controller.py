from .backend import PointerBackend
from .types import PointerPosition


class PointerController:
    """Controls when pointer positions are forwarded to the backend."""

    def __init__(self, backend: PointerBackend) -> None:
        if not callable(getattr(backend, "move", None)):
            raise TypeError("backend must provide a callable move method")

        self.backend = backend

    def process(
        self,
        position: PointerPosition | None,
        *,
        enabled: bool,
    ) -> bool:
        if not isinstance(enabled, bool):
            raise TypeError("enabled must be a bool")

        if not enabled or position is None:
            return False

        if not isinstance(position, PointerPosition):
            raise TypeError("position must be a PointerPosition or None")

        self.backend.move(position)
        return True