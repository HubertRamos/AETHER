import pytest

from aether.window_move.backend import (
    DryRunWindowMoveBackend,
    UmbrielWindowMoveBackend,
)


def test_dry_run_backend_records_window_moves():
    backend = DryRunWindowMoveBackend()
    backend.move_focused_window("left")
    backend.move_focused_window("right")
    assert backend.directions == ["left", "right"]


@pytest.mark.parametrize("direction", ["up", "down", ""])
def test_dry_run_backend_rejects_invalid_direction(direction):
    with pytest.raises(ValueError):
        DryRunWindowMoveBackend().move_focused_window(direction)


def test_umbriel_backend_sends_window_move_actions(monkeypatch):
    calls = []

    def fake_run(command, *, check, timeout):
        calls.append((command, check, timeout))

    monkeypatch.setattr("aether.window_move.backend.subprocess.run", fake_run)
    backend = UmbrielWindowMoveBackend()
    backend.move_focused_window("left")
    backend.move_focused_window("right")

    assert calls == [
        (["umbriel", "msg", "window-move-left"], True, 2),
        (["umbriel", "msg", "window-move-right"], True, 2),
    ]


def test_umbriel_backend_rejects_invalid_direction(monkeypatch):
    def unexpected_run(*args, **kwargs):
        pytest.fail("subprocess must not run for an invalid direction")

    monkeypatch.setattr(
        "aether.window_move.backend.subprocess.run",
        unexpected_run,
    )
    with pytest.raises(ValueError):
        UmbrielWindowMoveBackend().move_focused_window("up")
