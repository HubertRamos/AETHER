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
    assert pipeline.process(
        {"Left": Gesture.PINCH}, now=1.1, enabled=True
    ) == 1
    assert backend.clicks == [1]


def test_held_left_pinch_emits_only_one_click():
    pipeline, backend = create_pipeline()
    assert pipeline.process(
        {"Left": Gesture.PINCH}, now=1.0, enabled=True
    ) == 1
    assert pipeline.process(
        {"Left": Gesture.PINCH}, now=1.1, enabled=True
    ) == 0
    assert backend.clicks == [1]


def test_releasing_and_repeating_pinch_emits_another_click():
    pipeline, backend = create_pipeline()
    assert pipeline.process(
        {"Left": Gesture.PINCH}, now=1.0, enabled=True
    ) == 1
    assert pipeline.process(
        {"Left": Gesture.POINT}, now=1.1, enabled=True
    ) == 0
    assert pipeline.process(
        {"Left": Gesture.PINCH}, now=1.2, enabled=True
    ) == 1
    assert backend.clicks == [1, 1]


def test_suppressed_hand_does_not_click():
    pipeline, backend = create_pipeline()
    assert pipeline.process(
        {"Left": Gesture.PINCH}, now=1.0, enabled=True,
        suppressed_hands={"Left"},
    ) == 0
    assert backend.clicks == []


def test_disabled_pipeline_cancels_pinch_latch():
    pipeline, backend = create_pipeline()
    assert pipeline.process(
        {"Left": Gesture.PINCH}, now=1.0, enabled=True
    ) == 1
    assert pipeline.process(
        {"Left": Gesture.PINCH}, now=1.1, enabled=False
    ) == 0
    assert pipeline.process(
        {"Left": Gesture.PINCH}, now=1.2, enabled=True
    ) == 1
    assert backend.clicks == [1, 1]


def test_missing_hand_releases_pinch_latch():
    pipeline, backend = create_pipeline()
    assert pipeline.process(
        {"Left": Gesture.PINCH}, now=1.0, enabled=True
    ) == 1
    assert pipeline.process(
        {"Right": Gesture.POINT}, now=1.1, enabled=True
    ) == 0
    assert pipeline.process(
        {"Left": Gesture.PINCH}, now=1.2, enabled=True
    ) == 1
    assert backend.clicks == [1, 1]


def test_invalid_mapping_is_rejected():
    pipeline, _ = create_pipeline()
    with pytest.raises(TypeError):
        pipeline.process({"Left": "pinch"}, now=1.0, enabled=True)
