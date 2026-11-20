import pytest

from aether.pointer.backend import DryRunPointerBackend
from aether.pointer.types import PointerPosition


def test_records_pointer_movements():
    backend = DryRunPointerBackend()

    first = PointerPosition(0.2, 0.3)
    second = PointerPosition(0.8, 0.9)

    backend.move(first)
    backend.move(second)

    assert backend.positions == [first, second]


def test_rejects_invalid_position():
    backend = DryRunPointerBackend()

    with pytest.raises(TypeError):
        backend.move((0.5, 0.5))


def test_reset_clears_recorded_movements():
    backend = DryRunPointerBackend()
    backend.move(PointerPosition(0.5, 0.5))

    backend.reset()

    assert backend.positions == []
