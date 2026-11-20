
import pytest

from aether.actions import (
    Action,
    ActionExecutor,
    ActionRequest,
    DryRunBackend,
)
from aether.gestures.events import GestureEventType


def make_request(
    action=Action.POINTER,
    event_type=GestureEventType.GESTURE_STARTED,
    hand="Right",
    previous_action=None,
):
    return ActionRequest(
        hand=hand,
        action=action,
        event_type=event_type,
        previous_action=previous_action,
    )


def create_executor():
    backend = DryRunBackend()
    executor = ActionExecutor(backend)
    return executor, backend


def test_start_executes_request():
    executor, backend = create_executor()

    result = executor.process(make_request(), enabled=True)

    assert len(result) == 1
    assert len(backend.records) == 1
    assert executor.active_actions()["Right"] == Action.POINTER


def test_end_executes_request():
    executor, backend = create_executor()
    executor.process(make_request(), enabled=True)

    result = executor.process(
        make_request(event_type=GestureEventType.GESTURE_ENDED),
        enabled=True,
    )

    assert len(result) == 1
    assert backend.records[-1].event_type == GestureEventType.GESTURE_ENDED
    assert executor.active_actions() == {}


def test_change_executes_request():
    executor, backend = create_executor()
    executor.process(make_request(), enabled=True)

    request = make_request(
        action=Action.SELECT,
        event_type=GestureEventType.GESTURE_CHANGED,
        previous_action=Action.POINTER,
    )

    result = executor.process(request, enabled=True)

    assert len(result) == 1
    assert executor.active_actions()["Right"] == Action.SELECT
    assert backend.records[-1].previous_action == Action.POINTER


def test_ignores_duplicate_start():
    executor, backend = create_executor()
    executor.process(make_request(), enabled=True)

    result = executor.process(make_request(), enabled=True)

    assert result == ()
    assert len(backend.records) == 1


def test_ignores_start_with_previous_action():
    executor, backend = create_executor()

    result = executor.process(
        make_request(previous_action=Action.SELECT),
        enabled=True,
    )

    assert result == ()
    assert backend.records == []


def test_ignores_change_without_active_action():
    executor, backend = create_executor()

    result = executor.process(
        make_request(
            action=Action.SELECT,
            event_type=GestureEventType.GESTURE_CHANGED,
            previous_action=Action.POINTER,
        ),
        enabled=True,
    )

    assert result == ()
    assert backend.records == []


def test_ignores_change_with_stale_previous_action():
    executor, backend = create_executor()
    executor.process(make_request(), enabled=True)

    result = executor.process(
        make_request(
            action=Action.SELECT,
            event_type=GestureEventType.GESTURE_CHANGED,
            previous_action=Action.HOLD,
        ),
        enabled=True,
    )

    assert result == ()
    assert executor.active_actions()["Right"] == Action.POINTER


def test_ignores_change_to_same_action():
    executor, backend = create_executor()
    executor.process(make_request(), enabled=True)

    result = executor.process(
        make_request(
            event_type=GestureEventType.GESTURE_CHANGED,
            previous_action=Action.POINTER,
        ),
        enabled=True,
    )

    assert result == ()
    assert len(backend.records) == 1


def test_ignores_end_for_different_action():
    executor, backend = create_executor()
    executor.process(make_request(), enabled=True)

    result = executor.process(
        make_request(
            action=Action.SELECT,
            event_type=GestureEventType.GESTURE_ENDED,
        ),
        enabled=True,
    )

    assert result == ()
    assert executor.active_actions()["Right"] == Action.POINTER


def test_two_hands_are_independent():
    executor, backend = create_executor()

    executor.process(make_request(hand="Right"), enabled=True)
    executor.process(
        make_request(action=Action.SELECT, hand="Left"),
        enabled=True,
    )

    assert executor.active_actions() == {
        "Right": Action.POINTER,
        "Left": Action.SELECT,
    }


def test_deactivate_releases_all_actions():
    executor, backend = create_executor()

    executor.process(make_request(hand="Right"), enabled=True)
    executor.process(
        make_request(action=Action.SELECT, hand="Left"),
        enabled=True,
    )

    released = executor.deactivate()

    assert len(released) == 2
    assert executor.active_actions() == {}
    assert len(backend.records) == 4

    assert all(
        record.event_type == GestureEventType.GESTURE_ENDED
        for record in backend.records[-2:]
    )


def test_disabling_releases_active_action():
    executor, backend = create_executor()
    executor.process(make_request(), enabled=True)

    result = executor.process(make_request(), enabled=False)

    assert len(result) == 1
    assert result[0].event_type == GestureEventType.GESTURE_ENDED
    assert executor.active_actions() == {}


def test_disabling_without_actions_is_safe():
    executor, backend = create_executor()

    result = executor.process(None, enabled=False)

    assert result == ()
    assert backend.records == []


def test_none_request_does_nothing_when_enabled():
    executor, backend = create_executor()

    result = executor.process(None, enabled=True)

    assert result == ()
    assert backend.records == []


def test_active_actions_returns_copy():
    executor, backend = create_executor()
    executor.process(make_request(), enabled=True)

    snapshot = executor.active_actions()
    snapshot.clear()

    assert executor.active_actions() == {
        "Right": Action.POINTER
    }


def test_rejects_invalid_backend():
    with pytest.raises(TypeError):
        ActionExecutor(object())


def test_rejects_invalid_request():
    executor, backend = create_executor()

    with pytest.raises(TypeError):
        executor.process("invalid", enabled=True)


def test_rejects_invalid_enabled():
    executor, backend = create_executor()

    with pytest.raises(TypeError):
        executor.process(make_request(), enabled=1)


def test_rejects_invalid_hand():
    executor, backend = create_executor()

    with pytest.raises(ValueError):
        executor.process(
            make_request(hand=""),
            enabled=True,
        )
