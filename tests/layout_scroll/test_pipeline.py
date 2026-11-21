from unittest.mock import Mock

import pytest

from aether.gestures.types import Gesture
from aether.layout_scroll.controller import LayoutScrollController
from aether.layout_scroll.pipeline import LayoutScrollPipeline
from aether.pointer.types import PointerPosition


@pytest.fixture
def setup_pipeline():
    controller = LayoutScrollController(threshold=0.05, cooldown=0.1)
    backend = Mock()
    pipeline = LayoutScrollPipeline(controller, backend)
    return pipeline, controller, backend


def test_three_finger_pan_sends_horizontal_direction(setup_pipeline):
    pipeline, _, backend = setup_pipeline
    gesture = {"Right": Gesture.THREE_FINGER_PAN}

    assert pipeline.process(
        {"Right": PointerPosition(0.50, 0.5)},
        gesture,
        now=1.0,
        enabled=True,
    ) is None
    assert pipeline.process(
        {"Right": PointerPosition(0.56, 0.5)},
        gesture,
        now=1.1,
        enabled=True,
    ) == "right"
    backend.scroll.assert_called_once_with("right")


def test_three_finger_pan_can_scroll_left(setup_pipeline):
    pipeline, _, backend = setup_pipeline
    gesture = {"Right": Gesture.THREE_FINGER_PAN}
    pipeline.process(
        {"Right": PointerPosition(0.60, 0.5)},
        gesture,
        now=1.0,
        enabled=True,
    )
    assert pipeline.process(
        {"Right": PointerPosition(0.54, 0.5)},
        gesture,
        now=1.1,
        enabled=True,
    ) == "left"
    backend.scroll.assert_called_once_with("left")


@pytest.mark.parametrize(
    "gesture,enabled,suppressed",
    [
        (Gesture.TWO_FINGERS, True, set()),
        (Gesture.THREE_FINGER_PAN, False, set()),
        (Gesture.THREE_FINGER_PAN, True, {"Right"}),
    ],
)
def test_pan_requires_active_unsuppressed_three_finger_gesture(
    setup_pipeline, gesture, enabled, suppressed
):
    pipeline, controller, backend = setup_pipeline
    positions = {"Right": PointerPosition(0.5, 0.5)}
    pipeline.process(
        positions,
        {"Right": Gesture.THREE_FINGER_PAN},
        now=1.0,
        enabled=True,
    )
    result = pipeline.process(
        positions,
        {"Right": gesture},
        now=1.1,
        enabled=enabled,
        suppressed_hands=suppressed,
    )
    assert result is None
    assert controller.previous_x is None
    backend.scroll.assert_not_called()


def test_pan_resets_when_hand_disappears(setup_pipeline):
    pipeline, controller, backend = setup_pipeline
    pipeline.process(
        {"Right": PointerPosition(0.5, 0.5)},
        {"Right": Gesture.THREE_FINGER_PAN},
        now=1.0,
        enabled=True,
    )
    pipeline.process({}, {}, now=1.1, enabled=True)
    assert controller.previous_x is None
    backend.scroll.assert_not_called()
