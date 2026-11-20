
from unittest.mock import Mock

import pytest

from aether.gestures.types import Gesture
from aether.pointer.types import PointerPosition
from aether.scroll.controller import ScrollController
from aether.scroll.pipeline import ScrollPipeline


@pytest.fixture
def setup_pipeline():
    controller = ScrollController()
    backend = Mock()
    pipeline = ScrollPipeline(
        controller=controller,
        backend=backend,
    )
    return pipeline, controller, backend


def test_scroll_requires_two_fingers(setup_pipeline):
    pipeline, controller, backend = setup_pipeline

    positions = {"Right": PointerPosition(0.5, 0.5)}

    result = pipeline.process(
        positions,
        {"Right": Gesture.POINT},
        0.016,
        enabled=True,
    )

    assert result == (0, 0)
    backend.scroll.assert_not_called()
    assert controller.previous_position is None


def test_scroll_ignores_left_hand(setup_pipeline):
    pipeline, controller, backend = setup_pipeline

    positions = {"Left": PointerPosition(0.5, 0.5)}

    result = pipeline.process(
        positions,
        {"Left": Gesture.TWO_FINGERS},
        0.016,
        enabled=True,
    )

    assert result == (0, 0)
    backend.scroll.assert_not_called()


def test_scroll_requires_enabled(setup_pipeline):
    pipeline, controller, backend = setup_pipeline

    positions = {"Right": PointerPosition(0.5, 0.5)}

    pipeline.process(
        positions,
        {"Right": Gesture.TWO_FINGERS},
        0.016,
        enabled=False,
    )

    assert controller.previous_position is None
    backend.scroll.assert_not_called()


def test_scroll_reanchors_after_gesture_change(setup_pipeline):
    pipeline, controller, backend = setup_pipeline

    first = {"Right": PointerPosition(0.5, 0.5)}
    second = {"Right": PointerPosition(0.6, 0.5)}

    pipeline.process(
        first,
        {"Right": Gesture.TWO_FINGERS},
        0.016,
        enabled=True,
    )

    pipeline.process(
        second,
        {"Right": Gesture.POINT},
        0.016,
        enabled=True,
    )

    assert controller.previous_position is None

    pipeline.process(
        second,
        {"Right": Gesture.TWO_FINGERS},
        0.016,
        enabled=True,
    )

    assert controller.previous_position == (0.6, 0.5)
    backend.scroll.assert_not_called()


def test_scroll_resets_when_hand_disappears(setup_pipeline):
    pipeline, controller, backend = setup_pipeline

    pipeline.process(
        {"Right": PointerPosition(0.5, 0.5)},
        {"Right": Gesture.TWO_FINGERS},
        0.016,
        enabled=True,
    )

    pipeline.process(
        {},
        {},
        0.016,
        enabled=True,
    )

    assert controller.previous_position is None
    backend.scroll.assert_not_called()
