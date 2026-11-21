import pytest

from aether.click import ClickController, ClickPipeline
from aether.gestures.types import Gesture


class FakeClickBackend:
    def __init__(self):
        self.clicks = []
        self.buttons = []
        self.presses = []
        self.releases = []
        self.window_drag_starts = 0
        self.window_drag_ends = 0

    def press_window_drag(self):
        self.window_drag_starts += 1

    def release_window_drag(self):
        self.window_drag_ends += 1

    def click(self, count=1, button="left"):
        self.clicks.append(count)
        self.buttons.append(button)

    def press(self, button="left"):
        self.presses.append(button)

    def release(self, button="left"):
        self.releases.append(button)


def create_pipeline():
    backend = FakeClickBackend()
    return ClickPipeline(ClickController(), backend), backend


def test_only_left_hand_pinch_clicks():
    pipeline, backend = create_pipeline()
    assert pipeline.process({"Right": Gesture.PINCH}, now=1.0, enabled=True) == 0
    assert pipeline.process({"Left": Gesture.PINCH}, now=1.1, enabled=True) == 1
    assert backend.clicks == [1]


def test_held_left_pinch_emits_only_one_click():
    pipeline, backend = create_pipeline()
    pipeline.process({"Left": Gesture.PINCH}, now=1.0, enabled=True)
    pipeline.process({"Left": Gesture.PINCH}, now=1.1, enabled=True)
    assert backend.clicks == [1]


def test_releasing_and_repeating_pinch_emits_another_click():
    pipeline, backend = create_pipeline()
    pipeline.process({"Left": Gesture.PINCH}, now=1.0, enabled=True)
    pipeline.process({"Left": Gesture.POINT}, now=1.1, enabled=True)
    pipeline.process({"Left": Gesture.PINCH}, now=1.2, enabled=True)
    assert backend.clicks == [1, 1]


def test_suppressed_hand_does_not_click():
    pipeline, backend = create_pipeline()
    pipeline.process({"Left": Gesture.PINCH}, now=1.0, enabled=True, suppressed_hands={"Left"})
    assert backend.clicks == []


def test_disabled_pipeline_cancels_pinch_latch():
    pipeline, backend = create_pipeline()
    pipeline.process({"Left": Gesture.PINCH}, now=1.0, enabled=True)
    pipeline.process({"Left": Gesture.PINCH}, now=1.1, enabled=False)
    pipeline.process({"Left": Gesture.PINCH}, now=1.2, enabled=True)
    assert backend.clicks == [1, 1]


def test_missing_hand_releases_pinch_latch():
    pipeline, backend = create_pipeline()
    pipeline.process({"Left": Gesture.PINCH}, now=1.0, enabled=True)
    pipeline.process({"Right": Gesture.POINT}, now=1.1, enabled=True)
    pipeline.process({"Left": Gesture.PINCH}, now=1.2, enabled=True)
    assert backend.clicks == [1, 1]


def test_invalid_mapping_is_rejected():
    pipeline, _ = create_pipeline()
    with pytest.raises(TypeError):
        pipeline.process({"Left": "pinch"}, now=1.0, enabled=True)


def test_left_click_gesture_routes_left_button():
    pipeline, backend = create_pipeline()
    pipeline.process({"Left": Gesture.LEFT_CLICK}, now=1.0, enabled=True)
    assert backend.clicks == [1]
    assert backend.buttons == ["left"]


def test_right_click_gesture_routes_right_button():
    pipeline, backend = create_pipeline()
    pipeline.process({"Left": Gesture.RIGHT_CLICK}, now=1.0, enabled=True)
    assert backend.clicks == [1]
    assert backend.buttons == ["right"]


def test_click_gestures_are_only_read_from_left_hand():
    pipeline, backend = create_pipeline()
    pipeline.process({"Right": Gesture.RIGHT_CLICK}, now=1.0, enabled=True)
    assert backend.clicks == []


def test_left_press_and_release_are_sent_to_backend():
    pipeline, backend = create_pipeline()
    pipeline.process({"Left": Gesture.LEFT_PRESS}, now=1.0, enabled=True)
    pipeline.process({"Left": Gesture.POINT}, now=1.1, enabled=True)
    assert backend.presses == ["left"]
    assert backend.releases == ["left"]


def test_right_press_starts_and_ends_window_drag():
    pipeline, backend = create_pipeline()
    pipeline.process({"Left": Gesture.RIGHT_PRESS}, now=1.0, enabled=True)
    pipeline.process({"Left": Gesture.RIGHT_PRESS}, now=1.1, enabled=True)
    pipeline.process({"Left": Gesture.POINT}, now=1.2, enabled=True)
    assert backend.window_drag_starts == 1
    assert backend.window_drag_ends == 1
    assert backend.presses == []
    assert backend.releases == []


def test_held_button_is_released_when_hand_disappears():
    pipeline, backend = create_pipeline()
    pipeline.process({"Left": Gesture.LEFT_PRESS}, now=1.0, enabled=True)
    pipeline.process({"Right": Gesture.POINT}, now=1.1, enabled=True)
    assert backend.presses == ["left"]
    assert backend.releases == ["left"]


def test_switching_held_buttons_releases_old_and_presses_new():
    pipeline, backend = create_pipeline()
    pipeline.process({"Left": Gesture.LEFT_PRESS}, now=1.0, enabled=True)
    pipeline.process({"Left": Gesture.RIGHT_PRESS}, now=1.1, enabled=True)
    assert backend.presses == ["left"]
    assert backend.releases == ["left"]
    assert backend.window_drag_starts == 1
    assert backend.window_drag_ends == 0
