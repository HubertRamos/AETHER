
import pytest

from aether.gestures.tracker import HandTracker
from aether.gestures.types import Gesture


def test_tracks_two_hands_independently():
    tracker = HandTracker()

    result = {}

    for _ in range(4):
        result = tracker.update({
            "Left": Gesture.OPEN_PALM,
            "Right": Gesture.FIST,
        })

    assert result["Left"] == Gesture.OPEN_PALM
    assert result["Right"] == Gesture.FIST


def test_one_hand_disappearing_does_not_affect_other():
    tracker = HandTracker()

    for _ in range(4):
        tracker.update({
            "Left": Gesture.OPEN_PALM,
            "Right": Gesture.FIST,
        })

    result = {}

    for _ in range(4):
        result = tracker.update({
            "Right": Gesture.FIST,
        })

    assert "Left" in result
    assert result["Left"] == Gesture.OPEN_PALM
    assert result["Right"] == Gesture.FIST


def test_releases_hand_after_missing_frames():
    tracker = HandTracker(release_after_frames=3)

    for _ in range(4):
        tracker.update({"Left": Gesture.OPEN_PALM})

    tracker.update({})
    tracker.update({})

    assert "Left" in tracker.hands

    result = tracker.update({})

    assert "Left" not in result
    assert "Left" not in tracker.hands


def test_reappearing_hand_starts_with_fresh_state():
    tracker = HandTracker(release_after_frames=2)

    for _ in range(4):
        tracker.update({"Left": Gesture.OPEN_PALM})

    tracker.update({})
    tracker.update({})

    result = tracker.update({
        "Left": Gesture.FIST,
    })

    assert result["Left"] == Gesture.UNKNOWN


def test_reset_clears_all_hands():
    tracker = HandTracker()

    for _ in range(4):
        tracker.update({
            "Left": Gesture.OPEN_PALM,
            "Right": Gesture.FIST,
        })

    tracker.reset()

    assert tracker.hands == {}
    assert tracker.update({}) == {}


def test_invalid_release_configuration():
    with pytest.raises(ValueError):
        HandTracker(release_after_frames=0)


def test_rejects_invalid_gesture():
    tracker = HandTracker()

    with pytest.raises(TypeError):
        tracker.update({"Left": "open_palm"})


def test_hand_becomes_invisible_when_missing():
    tracker = HandTracker()

    tracker.update({
        "Right": Gesture.OPEN_PALM
    })

    tracker.update({})

    assert tracker.hands["Right"].visible is False


def test_hand_becomes_visible_when_detected():
    tracker = HandTracker()

    tracker.update({
        "Right": Gesture.OPEN_PALM
    })

    assert tracker.hands["Right"].visible is True


def test_visible_gestures_excludes_missing_hands():
    tracker = HandTracker()

    for _ in range(4):
        tracker.update({
            "Right": Gesture.OPEN_PALM,
            "Left": Gesture.FIST,
        })

    tracker.update({
        "Right": Gesture.OPEN_PALM
    })

    visible = tracker.visible_gestures()

    assert visible == {
        "Right": Gesture.OPEN_PALM
    }


def test_missing_hand_keeps_last_gesture_temporarily():
    tracker = HandTracker()

    for _ in range(4):
        tracker.update({
            "Right": Gesture.OPEN_PALM
        })

    tracker.update({})

    assert tracker.hands["Right"].gesture == Gesture.OPEN_PALM
    assert tracker.visible_gestures() == {}
