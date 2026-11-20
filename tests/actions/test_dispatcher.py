
import pytest

from aether.actions.dispatcher import ActionDispatcher
from aether.actions.types import Action
from aether.gestures.events import GestureEventType
from aether.gestures.mapping import Intent
from aether.intents.types import IntentStateEvent


def make_event(
    intent=Intent.POINT,
    event_type=GestureEventType.GESTURE_STARTED,
    hand="Right",
):
    return IntentStateEvent(
        hand=hand,
        intent=intent,
        event_type=event_type,
    )


def test_default_mapping():
    dispatcher = ActionDispatcher()

    result = dispatcher.dispatch(make_event(), enabled=True)

    assert result.action == Action.POINTER


def test_start_action():
    dispatcher = ActionDispatcher()

    result = dispatcher.dispatch(make_event(), enabled=True)

    assert result is not None
    assert result.event_type == GestureEventType.GESTURE_STARTED
    assert dispatcher.active_actions() == {
        "Right": Action.POINTER
    }


def test_end_action():
    dispatcher = ActionDispatcher()
    dispatcher.dispatch(make_event(), enabled=True)

    result = dispatcher.dispatch(
        make_event(event_type=GestureEventType.GESTURE_ENDED),
        enabled=True,
    )

    assert result is not None
    assert result.event_type == GestureEventType.GESTURE_ENDED
    assert dispatcher.active_actions() == {}


def test_change_action():
    dispatcher = ActionDispatcher()
    dispatcher.dispatch(make_event(), enabled=True)

    result = dispatcher.dispatch(
        make_event(
            intent=Intent.SELECT,
            event_type=GestureEventType.GESTURE_CHANGED,
        ),
        enabled=True,
    )

    assert result.action == Action.SELECT
    assert result.previous_action == Action.POINTER


def test_two_hands_are_independent():
    dispatcher = ActionDispatcher()

    dispatcher.dispatch(make_event(hand="Right"), enabled=True)
    dispatcher.dispatch(
        make_event(intent=Intent.SELECT, hand="Left"),
        enabled=True,
    )

    assert dispatcher.active_actions() == {
        "Right": Action.POINTER,
        "Left": Action.SELECT,
    }


def test_disabling_clears_actions():
    dispatcher = ActionDispatcher()
    dispatcher.dispatch(make_event(), enabled=True)

    result = dispatcher.dispatch(make_event(), enabled=False)

    assert result is None
    assert dispatcher.active_actions() == {}


def test_disabled_dispatcher_does_not_start():
    dispatcher = ActionDispatcher()

    result = dispatcher.dispatch(make_event(), enabled=False)

    assert result is None
    assert dispatcher.active_actions() == {}


def test_ignores_duplicate_start():
    dispatcher = ActionDispatcher()
    dispatcher.dispatch(make_event(), enabled=True)

    result = dispatcher.dispatch(make_event(), enabled=True)

    assert result is None


def test_ignores_end_without_active_action():
    dispatcher = ActionDispatcher()

    result = dispatcher.dispatch(
        make_event(event_type=GestureEventType.GESTURE_ENDED),
        enabled=True,
    )

    assert result is None


def test_ignores_change_without_active_action():
    dispatcher = ActionDispatcher()

    result = dispatcher.dispatch(
        make_event(event_type=GestureEventType.GESTURE_CHANGED),
        enabled=True,
    )

    assert result is None


def test_custom_mapping():
    dispatcher = ActionDispatcher({
        Intent.POINT: Action.SELECT,
    })

    result = dispatcher.dispatch(make_event(), enabled=True)

    assert result.action == Action.SELECT


def test_unmapped_intent():
    dispatcher = ActionDispatcher({
        Intent.SELECT: Action.SELECT,
    })

    result = dispatcher.dispatch(make_event(), enabled=True)

    assert result is None


def test_set_mapping():
    dispatcher = ActionDispatcher()
    dispatcher.set_mapping(Intent.POINT, Action.HOLD)

    result = dispatcher.dispatch(make_event(), enabled=True)

    assert result.action == Action.HOLD


def test_remove_mapping():
    dispatcher = ActionDispatcher()
    dispatcher.set_mapping(Intent.POINT, None)

    result = dispatcher.dispatch(make_event(), enabled=True)

    assert result is None


def test_reset():
    dispatcher = ActionDispatcher()
    dispatcher.dispatch(make_event(), enabled=True)

    dispatcher.reset()

    assert dispatcher.active_actions() == {}


def test_active_actions_returns_copy():
    dispatcher = ActionDispatcher()
    dispatcher.dispatch(make_event(), enabled=True)

    snapshot = dispatcher.active_actions()
    snapshot.clear()

    assert dispatcher.active_actions() == {
        "Right": Action.POINTER
    }


def test_rejects_invalid_event():
    dispatcher = ActionDispatcher()

    with pytest.raises(TypeError):
        dispatcher.dispatch("invalid", enabled=True)


def test_rejects_invalid_enabled():
    dispatcher = ActionDispatcher()

    with pytest.raises(TypeError):
        dispatcher.dispatch(make_event(), enabled=1)


def test_rejects_invalid_hand():
    dispatcher = ActionDispatcher()

    with pytest.raises(ValueError):
        dispatcher.dispatch(
            make_event(hand=""),
            enabled=True,
        )


def test_rejects_invalid_mapping():
    with pytest.raises(TypeError):
        ActionDispatcher({
            "point": Action.POINTER,
        })
