import pytest

from aether.pointer.types import PointerPosition


def test_accepts_valid_position():
    position = PointerPosition(0.5, 0.7)

    assert position.x == 0.5
    assert position.y == 0.7


@pytest.mark.parametrize(
    "x, y",
    [
        (0.0, 0.0),
        (1.0, 1.0),
        (0.0, 1.0),
        (1.0, 0.0),
    ],
)
def test_accepts_boundaries(x, y):
    assert PointerPosition(x, y)


@pytest.mark.parametrize("x, y", [(-0.1, 0.5), (1.1, 0.5), (0.5, -0.1), (0.5, 1.1)])
def test_rejects_out_of_range_coordinates(x, y):
    with pytest.raises(ValueError):
        PointerPosition(x, y)


@pytest.mark.parametrize("x, y", [(float("nan"), 0.5), (0.5, float("inf"))])
def test_rejects_non_finite_coordinates(x, y):
    with pytest.raises(ValueError):
        PointerPosition(x, y)


@pytest.mark.parametrize("x, y", [(True, 0.5), (0.5, False), ("0.5", 0.5)])
def test_rejects_non_numeric_coordinates(x, y):
    with pytest.raises(TypeError):
        PointerPosition(x, y)


def test_position_is_immutable():
    position = PointerPosition(0.5, 0.5)

    with pytest.raises(AttributeError):
        position.x = 0.8