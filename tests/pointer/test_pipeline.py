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
    pipeline = PointerPipeline(controller, pointer_hand="Right")

    return backend, pipeline


def test_moves_pointer_with_active_point_gesture(setup_pipeline):
    backend, pipeline = setup_pipeline
    position = PointerPosition(0.4, 0.6)

    result = pipeline.process(
        {"Right": position},
        {"Right": Gesture.POINT},
        enabled=True,
    )

    assert result is True
    assert backend.positions == [position]


def test_does_not_move_when_activation_is_disabled(setup_pipeline):
    backend, pipeline = setup_pipeline

    result = pipeline.process(
        {"Right": PointerPosition(0.4, 0.6)},
        {"Right": Gesture.POINT},
        enabled=False,
    )

    assert result is False
    assert backend.positions == []


def test_does_not_move_with_non_point_gesture(setup_pipeline):
    backend, pipeline = setup_pipeline

    result = pipeline.process(
        {"Right": PointerPosition(0.4, 0.6)},
        {"Right": Gesture.OPEN_PALM},
        enabled=True,
    )

    assert result is False
    assert backend.positions == []


def test_does_not_move_when_hand_is_not_visible(setup_pipeline):
    backend, pipeline = setup_pipeline

    result = pipeline.process(
        {},
        {"Right": Gesture.POINT},
        enabled=True,
    )

    assert result is False
    assert backend.positions == []


def test_does_not_move_when_gesture_is_missing(setup_pipeline):
    backend, pipeline = setup_pipeline

    result = pipeline.process(
        {"Right": PointerPosition(0.4, 0.6)},
        {},
        enabled=True,
    )

    assert result is False
    assert backend.positions == []


def test_does_not_move_when_hand_is_suppressed(setup_pipeline):
    backend, pipeline = setup_pipeline

    result = pipeline.process(
        {"Right": PointerPosition(0.4, 0.6)},
        {"Right": Gesture.POINT},
        enabled=True,
        suppressed_hands={"Right"},
    )

    assert result is False
    assert backend.positions == []


def test_ignores_non_selected_hand(setup_pipeline):
    backend, pipeline = setup_pipeline

    result = pipeline.process(
        {"Left": PointerPosition(0.8, 0.2)},
        {"Left": Gesture.POINT},
        enabled=True,
    )

    assert result is False
    assert backend.positions == []


def test_only_selected_hand_controls_pointer(setup_pipeline):
    backend, pipeline = setup_pipeline
    position = PointerPosition(0.3, 0.7)

    result = pipeline.process(
        {
            "Right": position,
            "Left": PointerPosition(0.8, 0.2),
        },
        {
            "Right": Gesture.POINT,
            "Left": Gesture.POINT,
        },
        enabled=True,
    )

    assert result is True
    assert backend.positions == [position]


def test_rejects_invalid_gesture(setup_pipeline):
    _, pipeline = setup_pipeline

    with pytest.raises(TypeError):
        pipeline.process(
            {"Right": PointerPosition(0.4, 0.6)},
            {"Right": "point"},
            enabled=True,
        )


def test_rejects_invalid_position(setup_pipeline):
    _, pipeline = setup_pipeline

    with pytest.raises(TypeError):
        pipeline.process(
            {"Right": (0.4, 0.6)},
            {"Right": Gesture.POINT},
            enabled=True,
        )