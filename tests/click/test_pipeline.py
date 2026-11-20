import pytest

from aether.click import ClickController, ClickPipeline
from aether.gestures.types import Gesture


class FakeClickBackend:
    def __init__(self):
        self.clicks = []

    def click(self, count=1):
        self.clicks.append(count)


def create_pipeline():
    backend = FakeClickBackend()
    pipeline = ClickPipeline(ClickController(), backend)
    return pipeline, backend


def test_only_left_hand_pinch_clicks():
    pipeline, backend = create_pipeline()
    assert pipeline.process(
        {"Right": Gesture.PINCH}, now=1.0, enabled=True
    ) == 0
    assert backend.clicks == []


def test_left_hand_single_click():
    pipeline, backend = create_pipeline()
    pipeline.process({"Left": Gesture.PINCH}, now=1.0, enabled=True)
    pipeline.process({"Left": Gesture.OPEN_PALM}, now=1.1, enabled=True)
    assert pipeline.process(
        {"Left": Gesture.OPEN_PALM}, now=1.39, enabled=True
    ) == 1
    assert backend.clicks == [1]


def test_left_hand_double_click():
    pipeline, backend = create_pipeline()
    pipeline.process({"Left": Gesture.PINCH}, now=1.0, enabled=True)
    pipeline.process({"Left": Gesture.OPEN_PALM}, now=1.05, enabled=True)
    pipeline.process({"Left": Gesture.PINCH}, now=1.15, enabled=True)
    assert pipeline.process(
        {"Left": Gesture.OPEN_PALM}, now=1.20, enabled=True
    ) == 2
    assert backend.clicks == [2]


def test_suppressed_hand_does_not_click():
    pipeline, backend = create_pipeline()
    assert pipeline.process(
        {"Left": Gesture.PINCH}, now=1.0, enabled=True,
        suppressed_hands={"Left"},
    ) == 0
    assert backend.clicks == []


def test_disabled_pipeline_cancels_pending_click():
    pipeline, backend = create_pipeline()
    pipeline.process({"Left": Gesture.PINCH}, now=1.0, enabled=True)
    pipeline.process({"Left": Gesture.OPEN_PALM}, now=1.1, enabled=True)
    pipeline.process({"Left": Gesture.OPEN_PALM}, now=1.2, enabled=False)
    assert backend.clicks == []


def test_missing_left_hand_cancels_pending_click():
    pipeline, backend = create_pipeline()
    pipeline.process({"Left": Gesture.PINCH}, now=1.0, enabled=True)
    pipeline.process({"Left": Gesture.OPEN_PALM}, now=1.1, enabled=True)
    pipeline.process({"Right": Gesture.POINT}, now=1.2, enabled=True)
    assert backend.clicks == []


def test_invalid_mapping_is_rejected():
    pipeline, _ = create_pipeline()
    with pytest.raises(TypeError):
        pipeline.process({"Left": "pinch"}, now=1.0, enabled=True)
