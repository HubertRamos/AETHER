
import pytest

from aether.gestures.stabilizer import GestureStabilizer
from aether.gestures.types import Gesture


def test_confirms_after_four_votes():
    stabilizer = GestureStabilizer()

    for _ in range(3):
        assert stabilizer.update(Gesture.OPEN_PALM) == Gesture.UNKNOWN

    assert stabilizer.update(Gesture.OPEN_PALM) == Gesture.OPEN_PALM


def test_ignores_transient_noise():
    stabilizer = GestureStabilizer()

    for _ in range(4):
        stabilizer.update(Gesture.OPEN_PALM)

    assert stabilizer.update(Gesture.FIST) == Gesture.OPEN_PALM


def test_switches_after_new_gesture_stabilizes():
    stabilizer = GestureStabilizer()

    for _ in range(4):
        stabilizer.update(Gesture.OPEN_PALM)

    for _ in range(4):
        result = stabilizer.update(Gesture.FIST)

    assert result == Gesture.FIST


def test_releases_after_tracking_loss():
    stabilizer = GestureStabilizer()

    for _ in range(4):
        stabilizer.update(Gesture.OPEN_PALM)

    for _ in range(7):
        assert stabilizer.update(Gesture.UNKNOWN) == Gesture.OPEN_PALM

    assert stabilizer.update(Gesture.UNKNOWN) == Gesture.UNKNOWN


def test_reset():
    stabilizer = GestureStabilizer()

    for _ in range(4):
        stabilizer.update(Gesture.OPEN_PALM)

    stabilizer.reset()

    assert stabilizer.current == Gesture.UNKNOWN


def test_invalid_configuration():
    with pytest.raises(ValueError):
        GestureStabilizer(window_size=5, min_votes=6)
