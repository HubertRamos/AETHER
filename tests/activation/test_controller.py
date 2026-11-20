
import pytest

from aether.activation.controller import ActivationController
from aether.activation.states import ActivationState


def test_starts_disabled():
    controller = ActivationController()

    assert controller.state == ActivationState.DISABLED
    assert controller.can_execute is False


def test_request_activation_enters_arming():
    controller = ActivationController()

    assert controller.request_activation() is True
    assert controller.state == ActivationState.ARMING
    assert controller.can_execute is False


def test_confirm_activation_enters_active():
    controller = ActivationController()

    controller.request_activation()

    assert controller.confirm_activation() is True
    assert controller.state == ActivationState.ACTIVE
    assert controller.can_execute is True


def test_activation_timeout_returns_to_disabled():
    controller = ActivationController(arming_timeout=5)

    controller.request_activation()
    controller.update(4)

    assert controller.state == ActivationState.ARMING

    controller.update(1)

    assert controller.state == ActivationState.DISABLED
    assert controller.can_execute is False


def test_cancel_activation():
    controller = ActivationController()

    controller.request_activation()
    controller.cancel_activation()

    assert controller.state == ActivationState.DISABLED
    assert controller.can_execute is False


def test_deactivation_enters_cooldown():
    controller = ActivationController()

    controller.request_activation()
    controller.confirm_activation()
    controller.deactivate()

    assert controller.state == ActivationState.COOLDOWN
    assert controller.can_execute is False


def test_cooldown_returns_to_disabled():
    controller = ActivationController(cooldown_duration=2)

    controller.request_activation()
    controller.confirm_activation()
    controller.deactivate()

    controller.update(1)

    assert controller.state == ActivationState.COOLDOWN

    controller.update(1)

    assert controller.state == ActivationState.DISABLED


def test_emergency_stop_blocks_execution():
    controller = ActivationController()

    controller.request_activation()
    controller.confirm_activation()
    controller.emergency_stop()

    assert controller.state == ActivationState.COOLDOWN
    assert controller.can_execute is False


def test_tracking_loss_blocks_execution():
    controller = ActivationController()

    controller.request_activation()
    controller.confirm_activation()
    controller.tracking_lost()

    assert controller.state == ActivationState.COOLDOWN
    assert controller.can_execute is False


def test_tracking_loss_during_arming_cancels_activation():
    controller = ActivationController()

    controller.request_activation()
    controller.tracking_lost()

    assert controller.state == ActivationState.DISABLED
    assert controller.can_execute is False


def test_cannot_confirm_without_arming():
    controller = ActivationController()

    assert controller.confirm_activation() is False
    assert controller.state == ActivationState.DISABLED


def test_cannot_activate_twice():
    controller = ActivationController()

    assert controller.request_activation() is True
    assert controller.request_activation() is False


@pytest.mark.parametrize(
    "arming_timeout,cooldown_duration",
    [
        (0, 1),
        (-1, 1),
        (1, 0),
        (1, -1),
        (float("inf"), 1),
        (1, float("nan")),
    ],
)
def test_invalid_durations(arming_timeout, cooldown_duration):
    with pytest.raises(ValueError):
        ActivationController(
            arming_timeout=arming_timeout,
            cooldown_duration=cooldown_duration,
        )


@pytest.mark.parametrize(
    "elapsed",
    [-1, float("inf"), float("nan")],
)
def test_invalid_elapsed_time(elapsed):
    controller = ActivationController()

    with pytest.raises(ValueError):
        controller.update(elapsed)
