import pytest

from aether.pointer.backend import DryRunPointerBackend
from aether.pointer.controller import PointerController
from aether.pointer.types import PointerPosition


def test_forwards_position_when_enabled():
    backend = DryRunPointerBackend()
    controller = PointerController(backend)
    position = PointerPosition(0.4, 0.6)

    result = controller.process(position, enabled=True)

    assert result is True
    assert backend.positions == [position]


def test_does_not_forward_position_when_disabled():
    backend = DryRunPointerBackend()
    controller = PointerController(backend)

    result = controller.process(
        PointerPosition(0.4, 0.6),
        enabled=False,
    )

    assert result is False
    assert backend.positions == []


def test_does_not_forward_missing_position():
    backend = DryRunPointerBackend()
    controller = PointerController(backend)

    result = controller.process(None, enabled=True)

    assert result is False
    assert backend.positions == []


def test_rejects_invalid_position():
    backend = DryRunPointerBackend()
    controller = PointerController(backend)

    with pytest.raises(TypeError):
        controller.process((0.4, 0.6), enabled=True)


def test_rejects_invalid_enabled_value():
    backend = DryRunPointerBackend()
    controller = PointerController(backend)

    with pytest.raises(TypeError):
        controller.process(
            PointerPosition(0.4, 0.6),
            enabled=1,
        )


def test_rejects_backend_without_move():
    with pytest.raises(TypeError):
        PointerController(object())