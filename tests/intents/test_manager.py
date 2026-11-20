
import pytest

from aether.gestures.events import GestureEventType
from aether.gestures.mapping import Intent, IntentEvent
from aether.intents.manager import IntentManager


def make_event(
    intent=Intent.POINT,
    event_type=GestureEventType.GESTURE_STARTED,
    hand="Right",
):
    return IntentEvent(
        intent=intent,
        hand=hand,
        event_type=event_type,
    )


def test_starts_intent():
    manager = IntentManager()

    result = manager.process(make_event())

    assert result is not None
    assert result.intent == Intent.POINT
    assert result.event_type == GestureEventType.GESTURE_STARTED
    assert manager.active_intents() == {"Right": Intent.POINT}


def test_ends_intent():
    manager = IntentManager()
    manager.process(make_event())

    result = manager.process(
        make_event(
            event_type=GestureEventType.GESTURE_ENDED,
        )
    )

    assert result is not None
    assert result.event_type == GestureEventType.GESTURE_ENDED
    assert manager.active_intents() == {}


def test_changes_intent():
    manager = IntentManager()
    manager.process(make_event())

    result = manager.process(
        make_event(
            intent=Intent.SELECT,
            event_type=GestureEventType.GESTURE_CHANGED,
        )
    )

    assert result is not None
    assert result.intent == Intent.SELECT
    assert result.previous_intent == Intent.POINT
    assert result.event_type == GestureEventType.GESTURE_CHANGED


def test_tracks_two_hands_independently():
    manager = IntentManager()

    manager.process(make_event(hand="Right"))
    manager.process(make_event(
        intent=Intent.SELECT,
        hand="Left",
    ))

    assert manager.active_intents() == {
        "Right": Intent.POINT,
        "Left": Intent.SELECT,
    }


def test_ending_one_hand_preserves_other():
    manager = IntentManager()
    manager.process(make_event(hand="Right"))
    manager.process(make_event(hand="Left"))

    manager.process(make_event(
        hand="Right",
        event_type=GestureEventType.GESTURE_ENDED,
    ))

    assert manager.active_intents() == {"Left": Intent.POINT}


def test_ignores_duplicate_start():
    manager = IntentManager()
    manager.process(make_event())

    result = manager.process(make_event())

    assert result is None
    assert manager.active_intents() == {"Right": Intent.POINT}


def test_start_replaces_existing_intent():
    manager = IntentManager()
    manager.process(make_event())

    result = manager.process(
        make_event(intent=Intent.SELECT)
    )

    assert result is not None
    assert result.event_type == GestureEventType.GESTURE_CHANGED
    assert result.previous_intent == Intent.POINT
    assert manager.active_intents() == {"Right": Intent.SELECT}


def test_ignores_change_without_active_intent():
    manager = IntentManager()

    result = manager.process(
        make_event(
            event_type=GestureEventType.GESTURE_CHANGED,
        )
    )

    assert result is None
    assert manager.active_intents() == {}


def test_ignores_ending_unknown_intent():
    manager = IntentManager()

    result = manager.process(
        make_event(
            event_type=GestureEventType.GESTURE_ENDED,
        )
    )

    assert result is None


def test_ignores_stale_end_event():
    manager = IntentManager()
    manager.process(make_event(intent=Intent.SELECT))

    result = manager.process(
        make_event(
            intent=Intent.POINT,
            event_type=GestureEventType.GESTURE_ENDED,
        )
    )

    assert result is None
    assert manager.active_intents() == {"Right": Intent.SELECT}


def test_ignores_change_to_same_intent():
    manager = IntentManager()
    manager.process(make_event())

    result = manager.process(
        make_event(
            intent=Intent.POINT,
            event_type=GestureEventType.GESTURE_CHANGED,
        )
    )

    assert result is None


def test_process_many():
    manager = IntentManager()

    results = manager.process_many([
        make_event(),
        make_event(
            intent=Intent.SELECT,
            event_type=GestureEventType.GESTURE_CHANGED,
        ),
        make_event(
            intent=Intent.SELECT,
            event_type=GestureEventType.GESTURE_ENDED,
        ),
    ])

    assert len(results) == 3
    assert results[0].event_type == GestureEventType.GESTURE_STARTED
    assert results[1].event_type == GestureEventType.GESTURE_CHANGED
    assert results[2].event_type == GestureEventType.GESTURE_ENDED
    assert manager.active_intents() == {}


def test_reset_clears_all_hands():
    manager = IntentManager()
    manager.process(make_event(hand="Right"))
    manager.process(make_event(hand="Left"))

    manager.reset()

    assert manager.active_intents() == {}


def test_active_intents_returns_copy():
    manager = IntentManager()
    manager.process(make_event())

    snapshot = manager.active_intents()
    snapshot.clear()

    assert manager.active_intents() == {"Right": Intent.POINT}


def test_rejects_invalid_event():
    manager = IntentManager()

    with pytest.raises(TypeError):
        manager.process("point")


def test_rejects_invalid_hand():
    manager = IntentManager()

    with pytest.raises(ValueError):
        manager.process(make_event(hand=""))


def test_rejects_non_list_in_process_many():
    manager = IntentManager()

    with pytest.raises(TypeError):
        manager.process_many((make_event(),))
