from aether.gestures.engine import GestureEngine
from aether.gestures.events import GestureEventType
from aether.gestures.types import Gesture


def test_detects_gesture_started():
    engine = GestureEngine()

    events = engine.update({
        "Right": Gesture.OPEN_PALM
    })

    assert len(events) == 1
    assert events[0].event_type == GestureEventType.GESTURE_STARTED
    assert events[0].gesture == Gesture.OPEN_PALM


def test_ignores_unchanged_gesture():
    engine = GestureEngine()

    engine.update({"Right": Gesture.OPEN_PALM})

    events = engine.update({
        "Right": Gesture.OPEN_PALM
    })

    assert events == []


def test_detects_gesture_changed():
    engine = GestureEngine()

    engine.update({"Right": Gesture.OPEN_PALM})

    events = engine.update({
        "Right": Gesture.POINT
    })

    assert len(events) == 1
    assert events[0].event_type == GestureEventType.GESTURE_CHANGED
    assert events[0].previous_gesture == Gesture.OPEN_PALM
    assert events[0].gesture == Gesture.POINT


def test_detects_gesture_ended():
    engine = GestureEngine()

    engine.update({"Right": Gesture.OPEN_PALM})

    events = engine.update({})

    assert len(events) == 1
    assert events[0].event_type == GestureEventType.GESTURE_ENDED


def test_tracks_hands_independently():
    engine = GestureEngine()

    events = engine.update({
        "Right": Gesture.OPEN_PALM,
        "Left": Gesture.FIST,
    })

    assert len(events) == 2

    events = engine.update({
        "Right": Gesture.OPEN_PALM,
    })

    assert len(events) == 1
    assert events[0].hand == "Left"
    assert events[0].event_type == GestureEventType.GESTURE_ENDED


def test_reset_clears_active_gestures():
    engine = GestureEngine()

    engine.update({"Right": Gesture.OPEN_PALM})
    engine.reset()

    events = engine.update({})

    assert events == []


def test_rejects_invalid_gesture():
    engine = GestureEngine()

    try:
        engine.update({"Right": "open_palm"})
    except TypeError:
        pass
    else:
        raise AssertionError("Deveria rejeitar gesto inválido.")