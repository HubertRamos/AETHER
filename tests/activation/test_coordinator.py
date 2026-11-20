
import pytest

from aether.activation.coordinator import ActivationCoordinator
from aether.activation.states import ActivationState
from aether.gestures.types import Gesture


def test_starts_disabled():
    coordinator = ActivationCoordinator()

    assert coordinator.state == ActivationState.DISABLED
    assert coordinator.can_execute is False


def test_keyboard_request_enters_arming():
    coordinator = ActivationCoordinator()

    assert coordinator.request_activation() is True
    assert coordinator.state == ActivationState.ARMING


def test_open_palm_confirms_after_release():
    coordinator = ActivationCoordinator()
    coordinator.request_activation()

    coordinator.update({"Right": Gesture.FIST}, 0.016)

    consumed = coordinator.update(
        {"Right": Gesture.OPEN_PALM},
        0.016,
    )

    assert consumed is True
    assert coordinator.state == ActivationState.ACTIVE
    assert coordinator.can_execute is True


def test_held_open_palm_does_not_confirm():
    coordinator = ActivationCoordinator()
    coordinator.request_activation()

    consumed = coordinator.update(
        {"Right": Gesture.OPEN_PALM},
        0.016,
    )

    assert consumed is False
    assert coordinator.state == ActivationState.ARMING


def test_fist_does_not_confirm_activation():
    coordinator = ActivationCoordinator()
    coordinator.request_activation()

    consumed = coordinator.update(
        {"Right": Gesture.FIST},
        0.016,
    )

    assert consumed is False
    assert coordinator.state == ActivationState.ARMING


def test_no_hand_during_arming_does_not_cancel():
    coordinator = ActivationCoordinator()
    coordinator.request_activation()

    coordinator.update({}, 0.016)

    assert coordinator.state == ActivationState.ARMING


def test_removing_selected_hand_cancels_activation():
    coordinator = ActivationCoordinator()
    coordinator.request_activation()

    coordinator.update(
        {"Right": Gesture.OPEN_PALM},
        0.016,
    )

    coordinator.update({}, 0.016)

    assert coordinator.state == ActivationState.DISABLED
    assert coordinator.can_execute is False

    # Reaparecer não deve recuperar a ativação cancelada.
    confirmed = coordinator.update(
        {"Right": Gesture.OPEN_PALM},
        0.016,
    )

    assert confirmed is False
    assert coordinator.state == ActivationState.DISABLED

def test_losing_all_hands_deactivates():
    coordinator = ActivationCoordinator()
    coordinator.request_activation()

    coordinator.update(
        {"Right": Gesture.FIST},
        0.016,
    )
    coordinator.update(
        {"Right": Gesture.OPEN_PALM},
        0.016,
    )
    coordinator.update({}, 0.016)

    assert coordinator.state == ActivationState.COOLDOWN
    assert coordinator.can_execute is False


def test_one_visible_hand_prevents_tracking_shutdown():
    coordinator = ActivationCoordinator()
    coordinator.request_activation()

    coordinator.update({"Right": Gesture.FIST}, 0.016)
    coordinator.update({"Right": Gesture.OPEN_PALM}, 0.016)

    coordinator.update(
        {"Left": Gesture.UNKNOWN},
        0.016,
    )

    assert coordinator.state == ActivationState.ACTIVE


def test_emergency_stop():
    coordinator = ActivationCoordinator()
    coordinator.request_activation()

    coordinator.update({"Right": Gesture.FIST}, 0.016)
    coordinator.update({"Right": Gesture.OPEN_PALM}, 0.016)

    coordinator.emergency_stop()

    assert coordinator.state == ActivationState.COOLDOWN
    assert coordinator.can_execute is False


def test_confirmation_gesture_is_consumed_only_once():
    coordinator = ActivationCoordinator()
    coordinator.request_activation()

    coordinator.update({"Right": Gesture.FIST}, 0.016)

    first = coordinator.update(
        {"Right": Gesture.OPEN_PALM},
        0.016,
    )

    second = coordinator.update(
        {"Right": Gesture.OPEN_PALM},
        0.016,
    )

    assert first is True
    assert second is False


def test_invalid_gesture_is_rejected():
    coordinator = ActivationCoordinator()

    with pytest.raises(TypeError):
        coordinator.update(
            {"Right": "open_palm"},
            0.016,
        )


def test_tracking_loss_during_arming_cancels_activation():
    coordinator = ActivationCoordinator()
    coordinator.request_activation()

    coordinator.update(
        {"Right": Gesture.FIST},
        0.016,
    )

    coordinator.update({}, 0.016)

    assert coordinator.state == ActivationState.DISABLED
    assert coordinator.can_execute is False

def test_confirmation_must_use_the_same_hand():
    coordinator = ActivationCoordinator()
    coordinator.request_activation()

    coordinator.update({"Right": Gesture.FIST}, 0.016)

    # A outra mão não pode confirmar.
    confirmed = coordinator.update(
        {
            "Right": Gesture.FIST,
            "Left": Gesture.OPEN_PALM,
        },
        0.016,
    )

    assert confirmed is False
    assert coordinator.state == ActivationState.ARMING

    # A mão original precisa apresentar a palma.
    confirmed = coordinator.update(
        {
            "Right": Gesture.OPEN_PALM,
            "Left": Gesture.OPEN_PALM,
        },
        0.016,
    )

    assert confirmed is True
    assert coordinator.state == ActivationState.ACTIVE


def test_selected_hand_disappearing_cancels_activation():
    coordinator = ActivationCoordinator()
    coordinator.request_activation()

    coordinator.update({"Right": Gesture.FIST}, 0.016)

    coordinator.update(
        {"Left": Gesture.OPEN_PALM},
        0.016,
    )

    assert coordinator.state == ActivationState.DISABLED
    assert coordinator.can_execute is False


def test_second_hand_cannot_replace_selected_hand():
    coordinator = ActivationCoordinator()
    coordinator.request_activation()

    coordinator.update({"Right": Gesture.OPEN_PALM}, 0.016)

    # A mão original ainda está visível, mas a outra já está fechada.
    coordinator.update(
        {
            "Right": Gesture.OPEN_PALM,
            "Left": Gesture.FIST,
        },
        0.016,
    )

    assert coordinator.state == ActivationState.ARMING

    # A mão original solta e volta à palma.
    coordinator.update(
        {
            "Right": Gesture.FIST,
            "Left": Gesture.FIST,
        },
        0.016,
    )

    confirmed = coordinator.update(
        {
            "Right": Gesture.OPEN_PALM,
            "Left": Gesture.OPEN_PALM,
        },
        0.016,
    )

    assert confirmed is True
    assert coordinator.state == ActivationState.ACTIVE
