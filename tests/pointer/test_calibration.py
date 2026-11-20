
import pytest

from aether.pointer.calibration import PointerCalibration
from aether.pointer.types import PointerPosition


def test_default_calibration_preserves_position():
    calibration = PointerCalibration()

    position = PointerPosition(0.4, 0.7)

    assert calibration.transform(position) == position


def test_maps_camera_region_to_screen_region():
    calibration = PointerCalibration(
        camera_left=0.2,
        camera_top=0.2,
        camera_right=0.8,
        camera_bottom=0.8,
    )

    result = calibration.transform(
        PointerPosition(0.5, 0.5)
    )

    assert result.x == pytest.approx(0.5)
    assert result.y == pytest.approx(0.5)


def test_clamps_positions_outside_camera_region():
    calibration = PointerCalibration(
        camera_left=0.2,
        camera_top=0.2,
        camera_right=0.8,
        camera_bottom=0.8,
    )

    assert calibration.transform(
        PointerPosition(0.0, 0.0)
    ) == PointerPosition(0.0, 0.0)

    assert calibration.transform(
        PointerPosition(1.0, 1.0)
    ) == PointerPosition(1.0, 1.0)


def test_maps_to_restricted_screen_region():
    calibration = PointerCalibration(
        screen_left=0.1,
        screen_top=0.2,
        screen_right=0.9,
        screen_bottom=0.8,
    )

    result = calibration.transform(
        PointerPosition(0.5, 0.5)
    )

    assert result == PointerPosition(0.5, 0.5)


def test_inverts_horizontal_axis():
    calibration = PointerCalibration(invert_x=True)

    result = calibration.transform(
        PointerPosition(0.2, 0.4)
    )

    assert result == PointerPosition(0.8, 0.4)


def test_inverts_vertical_axis():
    calibration = PointerCalibration(invert_y=True)

    result = calibration.transform(
        PointerPosition(0.4, 0.2)
    )

    assert result == PointerPosition(0.4, 0.8)


def test_rejects_invalid_camera_bounds():
    with pytest.raises(ValueError):
        PointerCalibration(
            camera_left=0.8,
            camera_right=0.2,
        )


def test_rejects_invalid_screen_bounds():
    with pytest.raises(ValueError):
        PointerCalibration(
            screen_top=0.9,
            screen_bottom=0.1,
        )


def test_rejects_invalid_position():
    calibration = PointerCalibration()

    with pytest.raises(TypeError):
        calibration.transform((0.5, 0.5))
