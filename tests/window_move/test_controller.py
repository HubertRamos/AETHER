import pytest

from aether.window_move.controller import WindowMoveController


def test_controller_waits_for_horizontal_threshold():
    controller = WindowMoveController(threshold=0.05, cooldown=0.1)
    assert controller.process(0.50, 1.0) is None
    assert controller.process(0.52, 1.01) is None
    assert controller.process(0.56, 1.02) == "right"


def test_controller_detects_leftward_movement():
    controller = WindowMoveController(threshold=0.05, cooldown=0.1)
    controller.process(0.60, 1.0)
    assert controller.process(0.54, 1.1) == "left"


def test_controller_rate_limits_repeated_moves():
    controller = WindowMoveController(threshold=0.05, cooldown=0.2)
    controller.process(0.50, 1.0)
    assert controller.process(0.56, 1.01) == "right"
    assert controller.process(0.50, 1.05) is None
    assert controller.process(0.44, 1.30) == "left"


def test_controller_reset_reanchors_hand():
    controller = WindowMoveController()
    controller.process(0.50, 1.0)
    controller.reset()
    assert controller.process(0.90, 1.1) is None


@pytest.mark.parametrize("threshold,cooldown", [(0, 0.1), (-1, 0.1), (0.1, -1)])
def test_controller_rejects_invalid_configuration(threshold, cooldown):
    with pytest.raises(ValueError):
        WindowMoveController(threshold=threshold, cooldown=cooldown)
