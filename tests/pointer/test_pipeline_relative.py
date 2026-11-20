
import pytest

from aether.gestures.types import Gesture
from aether.pointer.backend import DryRunPointerBackend
from aether.pointer.controller import PointerController
from aether.pointer.pipeline import PointerPipeline
from aether.pointer.types import PointerPosition


@pytest.fixture
def setup_pipeline():
    backend = DryRunPointerBackend()
    controller = PointerController(backend)

    pipeline = PointerPipeline(
        controller,
        pointer_hand="Right",
        smoothing_alpha=1.0,
        mode="relative",
        relative_sensitivity=2.0,
    )

    return backend, pipeline


def test_starts_pointer_at_screen_center(setup_pipeline):
    backend, pipeline = setup_pipeline

    pipeline.process(
        {"Right": PointerPosition(0.2, 0.3)},
        {"Right": Gesture.POINT},
        enabled=True,
    )

    assert backend.positions[-1] == PointerPosition(0.5, 0.5)


def test_moves_relative_to_initial_hand_position(setup_pipeline):
    backend, pipeline = setup_pipeline

    pipeline.process(
        {"Right": PointerPosition(0.2, 0.3)},
        {"Right": Gesture.POINT},
        enabled=True,
    )

    pipeline.process(
        {"Right": PointerPosition(0.3, 0.4)},
        {"Right": Gesture.POINT},
        enabled=True,
    )

    assert backend.positions[-1].x == pytest.approx(0.7)
    assert backend.positions[-1].y == pytest.approx(0.7)


def test_clamps_pointer_to_screen_boundaries(setup_pipeline):
    backend, pipeline = setup_pipeline

    pipeline.process(
        {"Right": PointerPosition(0.5, 0.5)},
        {"Right": Gesture.POINT},
        enabled=True,
    )

    pipeline.process(
        {"Right": PointerPosition(1.0, 1.0)},
        {"Right": Gesture.POINT},
        enabled=True,
    )

    assert backend.positions[-1] == PointerPosition(1.0, 1.0)


def test_resets_reference_when_control_is_disabled(setup_pipeline):
    backend, pipeline = setup_pipeline

    pipeline.process(
        {"Right": PointerPosition(0.2, 0.2)},
        {"Right": Gesture.POINT},
        enabled=True,
    )

    pipeline.process(
        {"Right": PointerPosition(0.8, 0.8)},
        {"Right": Gesture.POINT},
        enabled=False,
    )

    pipeline.process(
        {"Right": PointerPosition(0.8, 0.8)},
        {"Right": Gesture.POINT},
        enabled=True,
    )

    assert backend.positions[-1] == PointerPosition(0.5, 0.5)


def test_rejects_invalid_mode():
    backend = DryRunPointerBackend()
    controller = PointerController(backend)

    with pytest.raises(ValueError):
        PointerPipeline(
            controller,
            pointer_hand="Right",
            mode="invalid",
        )


def test_rejects_invalid_sensitivity():
    backend = DryRunPointerBackend()
    controller = PointerController(backend)

    with pytest.raises(ValueError):
        PointerPipeline(
            controller,
            pointer_hand="Right",
            mode="relative",
            relative_sensitivity=0,
        )
