
import pytest

from aether.gestures.types import Gesture
from aether.pointer.backend import DryRunPointerBackend
from aether.pointer.calibration import PointerCalibration
from aether.pointer.controller import PointerController
from aether.pointer.pipeline import PointerPipeline
from aether.pointer.types import PointerPosition


def create_pipeline(
    calibration: PointerCalibration,
    smoothing_alpha: float = 1.0,
):
    backend = DryRunPointerBackend()
    controller = PointerController(backend)

    pipeline = PointerPipeline(
        controller=controller,
        pointer_hand="Right",
        smoothing_alpha=smoothing_alpha,
        calibration=calibration,
    )

    return pipeline, backend


def test_pipeline_sends_calibrated_position_to_backend():
    calibration = PointerCalibration(
        camera_left=0.2,
        camera_top=0.2,
        camera_right=0.8,
        camera_bottom=0.8,
    )

    pipeline, backend = create_pipeline(calibration)

    pipeline.process(
        {"Right": PointerPosition(0.5, 0.5)},
        {"Right": Gesture.POINT},
        enabled=True,
    )

    assert len(backend.positions) == 1

    result = backend.positions[0]

    assert result.x == pytest.approx(0.5)
    assert result.y == pytest.approx(0.5)


def test_pipeline_applies_axis_inversion():
    calibration = PointerCalibration(invert_x=True)

    pipeline, backend = create_pipeline(calibration)

    pipeline.process(
        {"Right": PointerPosition(0.2, 0.4)},
        {"Right": Gesture.POINT},
        enabled=True,
    )

    result = backend.positions[0]

    assert result.x == pytest.approx(0.8)
    assert result.y == pytest.approx(0.4)


def test_pipeline_smooths_before_calibration():
    calibration = PointerCalibration(invert_x=True)

    pipeline, backend = create_pipeline(
        calibration,
        smoothing_alpha=0.5,
    )

    pipeline.process(
        {"Right": PointerPosition(0.2, 0.4)},
        {"Right": Gesture.POINT},
        enabled=True,
    )

    pipeline.process(
        {"Right": PointerPosition(0.8, 0.4)},
        {"Right": Gesture.POINT},
        enabled=True,
    )

    result = backend.positions[-1]

    # EMA: 0.2 + 0.5 * (0.8 - 0.2) = 0.5
    # Inversion: 1.0 - 0.5 = 0.5
    assert result.x == pytest.approx(0.5)
    assert result.y == pytest.approx(0.4)


def test_pipeline_does_not_move_when_gesture_is_not_point():
    pipeline, backend = create_pipeline(PointerCalibration())

    pipeline.process(
        {"Right": PointerPosition(0.5, 0.5)},
        {"Right": Gesture.POINT},
        enabled=True,
    )

    pipeline.process(
        {"Right": PointerPosition(0.8, 0.8)},
        {"Right": Gesture.OPEN_PALM},
        enabled=True,
    )

    assert len(backend.positions) == 1


def test_pipeline_does_not_move_when_hand_is_suppressed():
    pipeline, backend = create_pipeline(PointerCalibration())

    pipeline.process(
        {"Right": PointerPosition(0.5, 0.5)},
        {"Right": Gesture.POINT},
        enabled=True,
        suppressed_hands={"Right"},
    )

    assert backend.positions == []
