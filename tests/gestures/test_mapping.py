
import pytest

from aether.gestures.events import (
    GestureEvent,
    GestureEventType,
)
from aether.gestures.mapping import (
    DEFAULT_MAPPINGS,
    GestureMapper,
    Intent,
)
from aether.gestures.types import Gesture


def make_event(
    gesture,
    event_type=GestureEventType.GESTURE_STARTED,
    hand="Right",
):
    return GestureEvent(
        event_type=event_type,
        hand=hand,
        gesture=gesture,
    )


def test_default_mappings():
    mapper = GestureMapper()

    for gesture, intent in DEFAULT_MAPPINGS.items():
        result = mapper.map_event(make_event(gesture))

        assert result is not None
        assert result.intent == intent


def test_unknown_gesture_has_no_mapping():
    mapper = GestureMapper()

    result = mapper.map_event(make_event(Gesture.UNKNOWN))

    assert result is None


def test_gesture_ended_preserves_intent_event():
    mapper = GestureMapper()

    result = mapper.map_event(
        make_event(
            Gesture.POINT,
            GestureEventType.GESTURE_ENDED,
        )
    )

    assert result is not None
    assert result.intent == Intent.POINT
    assert result.event_type == GestureEventType.GESTURE_ENDED


def test_gesture_changed_produces_intent():
    mapper = GestureMapper()

    result = mapper.map_event(
        make_event(
            Gesture.PINCH,
            GestureEventType.GESTURE_CHANGED,
        )
    )

    assert result is not None
    assert result.intent == Intent.SELECT


def test_custom_mapping():
    mapper = GestureMapper({
        Gesture.POINT: Intent.SELECT,
    })

    result = mapper.map_event(make_event(Gesture.POINT))

    assert result.intent == Intent.SELECT


def test_unmapped_gesture_returns_none():
    mapper = GestureMapper({
        Gesture.POINT: Intent.SELECT,
    })

    assert mapper.map_event(make_event(Gesture.FIST)) is None


def test_set_mapping():
    mapper = GestureMapper()

    mapper.set_mapping(Gesture.FIST, Intent.SELECT)

    result = mapper.map_event(make_event(Gesture.FIST))

    assert result.intent == Intent.SELECT


def test_remove_mapping():
    mapper = GestureMapper()

    mapper.set_mapping(Gesture.POINT, None)

    assert mapper.map_event(make_event(Gesture.POINT)) is None


def test_reset_defaults():
    mapper = GestureMapper({
        Gesture.POINT: Intent.SELECT,
    })

    mapper.reset_defaults()

    result = mapper.map_event(make_event(Gesture.POINT))

    assert result.intent == Intent.POINT


def test_mapping_preserves_hand():
    mapper = GestureMapper()

    result = mapper.map_event(
        make_event(Gesture.PINCH, hand="Left")
    )

    assert result.hand == "Left"


def test_mapping_preserves_event_type():
    mapper = GestureMapper()

    result = mapper.map_event(
        make_event(
            Gesture.POINT,
            GestureEventType.GESTURE_CHANGED,
        )
    )

    assert result.event_type == GestureEventType.GESTURE_CHANGED


def test_maps_multiple_events():
    mapper = GestureMapper()

    events = [
        make_event(Gesture.POINT),
        make_event(Gesture.PINCH),
        make_event(Gesture.FIST),
    ]

    results = mapper.map_events(events)

    assert len(results) == 3
    assert [result.intent for result in results] == [
        Intent.POINT,
        Intent.SELECT,
        Intent.HOLD,
    ]


def test_rejects_invalid_event():
    mapper = GestureMapper()

    with pytest.raises(TypeError):
        mapper.map_event("point")


def test_rejects_invalid_mapping_key():
    with pytest.raises(TypeError):
        GestureMapper({"point": Intent.POINT})


def test_rejects_invalid_mapping_value():
    with pytest.raises(TypeError):
        GestureMapper({
            Gesture.POINT: "select",
        })


def test_rejects_invalid_set_mapping():
    mapper = GestureMapper()

    with pytest.raises(TypeError):
        mapper.set_mapping(Gesture.POINT, "select")


def test_rejects_non_list_events():
    mapper = GestureMapper()

    with pytest.raises(TypeError):
        mapper.map_events((make_event(Gesture.POINT),))
