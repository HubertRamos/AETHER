import pytest

from aether.click.controller import ClickController
from aether.gestures.types import Gesture


def test_pinch_emits_one_click_on_activation():
    assert ClickController().process(Gesture.PINCH, now=1.0) == 1


def test_held_pinch_does_not_repeat_clicks():
    controller = ClickController()
    assert controller.process(Gesture.PINCH, now=1.0) == 1
    assert controller.process(Gesture.PINCH, now=1.1) == 0
    assert controller.process(Gesture.PINCH, now=1.2) == 0


def test_new_pinch_after_release_emits_another_click():
    controller = ClickController()
    assert controller.process(Gesture.PINCH, now=1.0) == 1
    assert controller.process(Gesture.POINT, now=1.1) == 0
    assert controller.process(Gesture.PINCH, now=1.2) == 1


def test_lost_hand_resets_pinch_latch():
    controller = ClickController()
    controller.process(Gesture.PINCH, now=1.0)
    controller.process(Gesture.UNKNOWN, now=1.1, hand_visible=False)
    assert controller.process(Gesture.PINCH, now=1.2) == 1


def test_disabling_resets_pinch_latch():
    controller = ClickController()
    controller.process(Gesture.PINCH, now=1.0)
    controller.process(Gesture.PINCH, now=1.1, enabled=False)
    assert controller.process(Gesture.PINCH, now=1.2) == 1


def test_invalid_inputs_are_rejected():
    controller = ClickController()
    with pytest.raises(TypeError):
        controller.process("pinch", now=1.0)
    with pytest.raises(ValueError):
        controller.process(Gesture.PINCH, now=float("nan"))
    with pytest.raises(ValueError):
        ClickController(double_click_interval=0)


def test_left_click_gesture_emits_one_left_click():
    controller = ClickController()
    assert controller.process(Gesture.LEFT_CLICK, now=1.0) == 1
    assert controller.active_button == "left"
    assert controller.process(Gesture.LEFT_CLICK, now=1.1) == 0


def test_right_click_gesture_emits_one_right_click():
    controller = ClickController()
    assert controller.process(Gesture.RIGHT_CLICK, now=1.0) == 1
    assert controller.active_button == "right"
    assert controller.process(Gesture.RIGHT_CLICK, now=1.1) == 0


def test_pinch_remains_left_click():
    controller = ClickController()
    assert controller.process(Gesture.PINCH, now=1.0) == 1
    assert controller.active_button == "left"


def test_switching_from_left_to_right_emits_new_click():
    controller = ClickController()
    controller.process(Gesture.LEFT_CLICK, now=1.0)
    assert controller.process(Gesture.RIGHT_CLICK, now=1.1) == 1
    assert controller.active_button == "right"


@pytest.mark.parametrize(("gesture", "button"), [
    (Gesture.LEFT_PRESS, "left"),
    (Gesture.RIGHT_PRESS, "right"),
])
def test_press_gesture_enters_held_state(gesture, button):
    controller = ClickController()
    assert controller.process(gesture, now=1.0) == 0
    assert controller.pressed_button == button
    assert controller.process(gesture, now=1.1) == 0
    assert controller.pressed_button == button


@pytest.mark.parametrize(("press", "release", "button"), [
    (Gesture.LEFT_PRESS, Gesture.POINT, "left"),
    (Gesture.RIGHT_PRESS, Gesture.POINT, "right"),
])
def test_releasing_press_gesture_clears_held_state(press, release, button):
    controller = ClickController()
    controller.process(press, now=1.0)
    controller.process(release, now=1.1)
    assert controller.pressed_button is None
    assert controller.released_button == button


def test_losing_hand_requests_release():
    controller = ClickController()
    controller.process(Gesture.LEFT_PRESS, now=1.0)
    controller.process(Gesture.UNKNOWN, now=1.1, hand_visible=False)
    assert controller.released_button == "left"
