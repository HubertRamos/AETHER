from __future__ import annotations

from math import acos, degrees, hypot
from typing import Sequence

from .types import Gesture


Point = tuple[float, float, float]


def _point(landmark) -> Point:
    """Converte um landmark do MediaPipe ou uma tupla em coordenadas."""
    if hasattr(landmark, "x"):
        return landmark.x, landmark.y, landmark.z
    return tuple(landmark)


def _distance(a: Point, b: Point) -> float:
    return hypot(a[0] - b[0], a[1] - b[1])


def _angle(a: Point, b: Point, c: Point) -> float:
    """Calcula o ângulo ABC em graus."""
    ba = (a[0] - b[0], a[1] - b[1])
    bc = (c[0] - b[0], c[1] - b[1])
    magnitude = hypot(*ba) * hypot(*bc)
    if magnitude < 1e-9:
        return 0.0
    cosine = (ba[0] * bc[0] + ba[1] * bc[1]) / magnitude
    cosine = max(-1.0, min(1.0, cosine))
    return degrees(acos(cosine))


def _finger_extended(points: Sequence[Point], mcp: int, pip: int, dip: int) -> bool:
    return _angle(points[mcp], points[pip], points[dip]) >= 150.0


def classify(
    landmarks,
    image_aspect_ratio: float = 4 / 3,
    pinch_threshold: float = 0.25,
    hand: str | None = None,
) -> Gesture:
    """Classifica uma mão e resolve gestos contextuais quando hand é informado.

    A pose TWO_FINGERS permanece disponível para a mão direita. Na mão
    esquerda, a mesma pose com o polegar recolhido representa LEFT_PRESS.
    """
    if len(landmarks) != 21:
        raise ValueError("Uma mão precisa conter exatamente 21 landmarks.")
    if image_aspect_ratio <= 0:
        raise ValueError("Aspect ratio deve ser positivo.")
    if not 0.0 <= pinch_threshold <= 1.0:
        raise ValueError("pinch_threshold deve estar entre 0 e 1.")
    if hand not in (None, "Left", "Right"):
        raise ValueError("hand deve ser 'Left', 'Right' ou None.")

    points = [_point(landmark) for landmark in landmarks]
    points = [(x * image_aspect_ratio, y, z * image_aspect_ratio) for x, y, z in points]
    palm_width = _distance(points[5], points[17])
    if palm_width < 1e-6:
        return Gesture.UNKNOWN

    index = _finger_extended(points, 5, 6, 7)
    middle = _finger_extended(points, 9, 10, 11)
    ring = _finger_extended(points, 13, 14, 15)
    pinky = _finger_extended(points, 17, 18, 19)

    thumb_angle = _angle(points[1], points[2], points[3])
    thumb_distance = _distance(points[4], points[5]) / palm_width
    thumb = thumb_angle >= 145.0 and thumb_distance >= 0.45

    pinch_distance = _distance(points[4], points[8]) / palm_width
    if pinch_distance <= pinch_threshold:
        return Gesture.PINCH

    # A pose de dois dedos é contextual: na mão esquerda, com o polegar
    # recolhido, segura o botão esquerdo; na direita, continua rolando.
    if hand == "Left" and not thumb and index and middle and not ring and not pinky:
        return Gesture.LEFT_PRESS
    if hand == "Left" and not thumb and not index and not middle and ring and pinky:
        return Gesture.RIGHT_PRESS

    if thumb and index and middle and not ring and not pinky:
        return Gesture.LEFT_CLICK
    if thumb and not index and not middle and ring and pinky:
        return Gesture.RIGHT_CLICK

    if thumb and index and middle and ring and pinky:
        return Gesture.OPEN_PALM
    if not thumb and not index and not middle and not ring and not pinky:
        return Gesture.FIST
    if index and not middle and not ring and not pinky:
        return Gesture.POINT
    if hand == "Right" and index and middle and ring and not pinky:
        return Gesture.THREE_FINGER_PAN
    if index and middle and not ring and not pinky:
        return Gesture.TWO_FINGERS
    return Gesture.UNKNOWN
