
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

    cosine = (
        ba[0] * bc[0] + ba[1] * bc[1]
    ) / magnitude

    cosine = max(-1.0, min(1.0, cosine))

    return degrees(acos(cosine))


def _finger_extended(
    points: Sequence[Point],
    mcp: int,
    pip: int,
    dip: int,
) -> bool:
    angle = _angle(
        points[mcp],
        points[pip],
        points[dip],
    )

    return angle >= 150.0


def classify(
    landmarks,
    image_aspect_ratio: float = 4 / 3,
    pinch_threshold: float = 0.25,
) -> Gesture:
    """
    Classifica uma mão usando os 21 landmarks do MediaPipe.

    image_aspect_ratio = largura / altura da imagem.
    """

    if len(landmarks) != 21:
        raise ValueError(
            "Uma mão precisa conter exatamente 21 landmarks."
        )

    if image_aspect_ratio <= 0:
        raise ValueError("Aspect ratio deve ser positivo.")

    if not 0.0 <= pinch_threshold <= 1.0:
        raise ValueError("pinch_threshold deve estar entre 0 e 1.")

    points = [
        _point(landmark)
        for landmark in landmarks
    ]

    # Corrige a diferença de escala entre os eixos X e Y.
    points = [
        (x * image_aspect_ratio, y, z * image_aspect_ratio)
        for x, y, z in points
    ]

    palm_width = _distance(points[5], points[17])

    if palm_width < 1e-6:
        return Gesture.UNKNOWN

    # Dedos: indicador, médio, anelar e mínimo.
    index = _finger_extended(points, 5, 6, 7)
    middle = _finger_extended(points, 9, 10, 11)
    ring = _finger_extended(points, 13, 14, 15)
    pinky = _finger_extended(points, 17, 18, 19)

    # Polegar: ângulo da articulação e distância relativa.
    thumb_angle = _angle(
        points[1],
        points[2],
        points[3],
    )

    thumb_distance = (
        _distance(points[4], points[5]) / palm_width
    )

    thumb = (
        thumb_angle >= 145.0
        and thumb_distance >= 0.45
    )

    # Pinch: aproximação entre polegar e indicador.
    pinch_distance = (
        _distance(points[4], points[8]) / palm_width
    )

    if pinch_distance <= pinch_threshold:
        return Gesture.PINCH

    # Gestos de mouse: polegar também precisa estar estendido.
    if thumb and index and middle and not ring and not pinky:
        return Gesture.LEFT_CLICK

    if thumb and not index and not middle and ring and pinky:
        return Gesture.RIGHT_CLICK

    # Classificação dos gestos.
    if thumb and index and middle and ring and pinky:
        return Gesture.OPEN_PALM

    if not thumb and not index and not middle and not ring and not pinky:
        return Gesture.FIST

    if index and not middle and not ring and not pinky:
        return Gesture.POINT

    if index and middle and not ring and not pinky:
        return Gesture.TWO_FINGERS

    return Gesture.UNKNOWN
