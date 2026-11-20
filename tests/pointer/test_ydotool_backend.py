
from unittest.mock import patch

import pytest

from aether.pointer import PointerPosition, YdotoolPointerBackend


def test_converts_normalized_position_to_screen_pixels():
    backend = YdotoolPointerBackend(1366, 768)

    with patch("aether.pointer.backend.subprocess.run") as run:
        backend.move(PointerPosition(0.5, 0.5))

    run.assert_called_once_with(
        [
            "ydotool",
            "mousemove",
            "--absolute",
            "--xpos",
            "682",
            "--ypos",
            "384",
        ],
        check=True,
        timeout=2,
    )


def test_maps_top_left_corner():
    backend = YdotoolPointerBackend(1366, 768)

    with patch("aether.pointer.backend.subprocess.run") as run:
        backend.move(PointerPosition(0.0, 0.0))

    args = run.call_args.args[0]
    assert args[args.index("--xpos") + 1] == "0"
    assert args[args.index("--ypos") + 1] == "0"

def test_maps_bottom_right_corner():
    backend = YdotoolPointerBackend(1366, 768)

    with patch("aether.pointer.backend.subprocess.run") as run:
        backend.move(PointerPosition(1.0, 1.0))

    args = run.call_args.args[0]
    assert args[-1] == "767"
    assert args[args.index("--xpos") + 1] == "1365"


def test_rejects_invalid_screen_dimensions():
    with pytest.raises(ValueError):
        YdotoolPointerBackend(0, 768)

    with pytest.raises(ValueError):
        YdotoolPointerBackend(1366, -1)


def test_rejects_invalid_position():
    backend = YdotoolPointerBackend(1366, 768)

    with pytest.raises(TypeError):
        backend.move((0.5, 0.5))
