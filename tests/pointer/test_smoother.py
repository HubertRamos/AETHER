
import pytest

from aether.pointer.smoother import PointerSmoother
from aether.pointer.types import PointerPosition


def test_first_position_is_returned_unchanged():
    smoother = PointerSmoother()

    position = PointerPosition(0.4, 0.6)

    assert smoother.process(position) == position


def test_smooths_subsequent_positions():
    smoother = PointerSmoother(alpha=0.5)

    smoother.process(PointerPosition(0.2, 0.2))

    result = smoother.process(PointerPosition(0.8, 0.8))

    assert result == PointerPosition(0.5, 0.5)


def test_alpha_one_disables_smoothing():
    smoother = PointerSmoother(alpha=1.0)

    smoother.process(PointerPosition(0.2, 0.2))

    position = PointerPosition(0.8, 0.7)

    assert smoother.process(position) == position


def test_reset_clears_previous_position():
    smoother = PointerSmoother(alpha=0.5)

    smoother.process(PointerPosition(0.2, 0.2))
    smoother.reset()

    position = PointerPosition(0.8, 0.8)

    assert smoother.process(position) == position


@pytest.mark.parametrize("alpha", [0, -0.1, 1.1, float("inf"), float("nan")])
def test_rejects_invalid_alpha(alpha):
    with pytest.raises(ValueError):
        PointerSmoother(alpha)


def test_rejects_boolean_alpha():
    with pytest.raises(TypeError):
        PointerSmoother(True)


def test_rejects_invalid_position():
    smoother = PointerSmoother()

    with pytest.raises(TypeError):
        smoother.process((0.4, 0.6))
