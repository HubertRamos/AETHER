
import pytest

from aether.gestures.classifier import classify
from aether.gestures.types import Gesture


def make_hand(
    extended=(False, False, False, False),
    thumb_extended=False,
    pinch=False,
):
    """Cria uma mão sintética com 21 landmarks."""

    points = [(0.5, 0.8, 0.0)] * 21

    # Pulso e palma.
    points[0] = (0.50, 0.85, 0.0)
    points[1] = (0.40, 0.65, 0.0)
    points[2] = (0.35, 0.60, 0.0)
    points[3] = (0.30, 0.55, 0.0)
    points[4] = (
        (0.40, 0.50, 0.0)
        if thumb_extended
        else (0.48, 0.68, 0.0)
    )

    # Articulações dos dedos.
    fingers = [
        (5, 6, 7, 8),
        (9, 10, 11, 12),
        (13, 14, 15, 16),
        (17, 18, 19, 20),
    ]

    bases = [0.42, 0.50, 0.58, 0.66]

    for is_extended, indices, base in zip(
        extended, fingers, bases
    ):
        mcp, pip, dip, tip = indices

        points[mcp] = (base, 0.65, 0.0)

        if is_extended:
            points[pip] = (base, 0.48, 0.0)
            points[dip] = (base, 0.34, 0.0)
            points[tip] = (base, 0.20, 0.0)
        else:
            points[pip] = (base, 0.52, 0.0)
            points[dip] = (base + 0.05, 0.56, 0.0)
            points[tip] = (base + 0.10, 0.60, 0.0)

    if pinch:
        points[4] = points[8]

    return points


def test_open_palm():
    hand = make_hand(
        extended=(True, True, True, True),
        thumb_extended=True,
    )
    assert classify(hand) == Gesture.OPEN_PALM


def test_fist():
    hand = make_hand()
    assert classify(hand) == Gesture.FIST


def test_point():
    hand = make_hand(extended=(True, False, False, False))
    assert classify(hand) == Gesture.POINT


def test_two_fingers():
    hand = make_hand(extended=(True, True, False, False))
    assert classify(hand) == Gesture.TWO_FINGERS


def test_pinch():
    hand = make_hand(pinch=True)
    assert classify(hand) == Gesture.PINCH


def test_invalid_landmark_count():
    with pytest.raises(ValueError):
        classify([(0.0, 0.0, 0.0)] * 10)


def test_invalid_aspect_ratio():
    with pytest.raises(ValueError):
        classify(make_hand(), image_aspect_ratio=0)


def test_degenerate_palm():
    hand = [(0.5, 0.5, 0.0)] * 21
    assert classify(hand) == Gesture.UNKNOWN


def transform_hand(hand, scale=1.0, angle=0.0):
    """Aplica escala e rotação 2D nos landmarks."""
    import math

    cosine = math.cos(angle)
    sine = math.sin(angle)

    transformed = []

    for x, y, z in hand:
        x -= 0.5
        y -= 0.5

        new_x = (x * cosine - y * sine) * scale
        new_y = (x * sine + y * cosine) * scale

        transformed.append((
            new_x + 0.5,
            new_y + 0.5,
            z * scale,
        ))

    return transformed


@pytest.mark.parametrize("scale", [0.6, 1.0, 1.5])
def test_open_palm_different_scales(scale):
    hand = make_hand(
        extended=(True, True, True, True),
        thumb_extended=True,
    )

    transformed = transform_hand(hand, scale=scale)

    assert classify(transformed) == Gesture.OPEN_PALM


@pytest.mark.parametrize("angle", [-0.3, 0.3, 0.6])
def test_point_with_rotation(angle):
    hand = make_hand(
        extended=(True, False, False, False)
    )

    transformed = transform_hand(hand, angle=angle)

    assert classify(transformed) == Gesture.POINT
