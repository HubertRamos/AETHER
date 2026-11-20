import pytest

from aether.click.controller import ClickController
from aether.gestures.types import Gesture


def test_single_click_waits_for_double_click_window():
    controller = ClickController()
    assert controller.process(Gesture.PINCH, now=1.0) == 0
    assert controller.process(Gesture.OPEN_PALM, now=1.1) == 0
    assert controller.process(Gesture.OPEN_PALM, now=1.39) == 1


def test_two_quick_pinches_emit_one_double_click():
    controller = ClickController()
    assert controller.process(Gesture.PINCH, now=1.0) == 0
    assert controller.process(Gesture.OPEN_PALM, now=1.08) == 0
    assert controller.process(Gesture.PINCH, now=1.20) == 0
    assert controller.process(Gesture.OPEN_PALM, now=1.28) == 2


def test_second_pinch_outside_window_emits_two_single_clicks():
    controller = ClickController()
    assert controller.process(Gesture.PINCH, now=1.0) == 0
    assert controller.process(Gesture.OPEN_PALM, now=1.05) == 0
    assert controller.process(Gesture.PINCH, now=1.40) == 1
    assert controller.process(Gesture.OPEN_PALM, now=1.48) == 0
    assert controller.process(Gesture.OPEN_PALM, now=1.77) == 1


def test_long_pinch_does_not_click():
    controller = ClickController()
    assert controller.process(Gesture.PINCH, now=1.0) == 0
    assert controller.process(Gesture.PINCH, now=1.3) == 0
    assert controller.process(Gesture.OPEN_PALM, now=1.31) == 0


def test_long_second_pinch_preserves_first_single_click():
    controller = ClickController()
    controller.process(Gesture.PINCH, now=1.0)
    controller.process(Gesture.OPEN_PALM, now=1.05)
    controller.process(Gesture.PINCH, now=1.15)
    assert controller.process(Gesture.OPEN_PALM, now=1.5) == 1


def test_held_pinch_does_not_repeat():
    controller = ClickController()
    assert controller.process(Gesture.PINCH, now=1.0) == 0
    assert controller.process(Gesture.PINCH, now=1.1) == 0
    assert controller.process(Gesture.OPEN_PALM, now=1.15) == 0
    assert controller.process(Gesture.OPEN_PALM, now=1.44) == 1


def test_lost_hand_cancels_pending_click():
    controller = ClickController()
    controller.process(Gesture.PINCH, now=1.0)
    controller.process(Gesture.OPEN_PALM, now=1.1)
    assert controller.process(
        Gesture.UNKNOWN, now=1.2, hand_visible=False
    ) == 0
    assert controller.process(Gesture.OPEN_PALM, now=2.0) == 0


def test_disabling_cancels_pending_click():
    controller = ClickController()
    controller.process(Gesture.PINCH, now=1.0)
    controller.process(Gesture.OPEN_PALM, now=1.1)
    assert controller.process(
        Gesture.OPEN_PALM, now=1.2, enabled=False
    ) == 0


def test_invalid_inputs_are_rejected():
    controller = ClickController()
    with pytest.raises(TypeError):
        controller.process("pinch", now=1.0)
    with pytest.raises(ValueError):
        controller.process(Gesture.PINCH, now=float("nan"))
    with pytest.raises(ValueError):
        ClickController(double_click_interval=0)
