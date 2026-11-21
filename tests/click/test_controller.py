import pytest

from aether.click.controller import ClickController
from aether.gestures.types import Gesture


def test_pinch_emits_one_click_on_activation():
    controller = ClickController()
    assert controller.process(Gesture.PINCH, now=1.0) == 1


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
    assert controller.process(Gesture.PINCH, now=1.0) == 1
    assert controller.process(
        Gesture.UNKNOWN, now=1.1, hand_visible=False
    ) == 0
    assert controller.process(Gesture.PINCH, now=1.2) == 1


def test_disabling_resets_pinch_latch():
    controller = ClickController()
    assert controller.process(Gesture.PINCH, now=1.0) == 1
    assert controller.process(
        Gesture.PINCH, now=1.1, enabled=False
    ) == 0
    assert controller.process(Gesture.PINCH, now=1.2) == 1


def test_invalid_inputs_are_rejected():
    controller = ClickController()
    with pytest.raises(TypeError):
        controller.process("pinch", now=1.0)
    with pytest.raises(ValueError):
        controller.process(Gesture.PINCH, now=float("nan"))
    with pytest.raises(ValueError):
        ClickController(double_click_interval=0)
