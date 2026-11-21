import pytest

from aether.layout_scroll.backend import (
    DryRunLayoutScrollBackend,
    UmbrielLayoutScrollBackend,
)


def test_dry_run_backend_records_pan_direction():
    backend = DryRunLayoutScrollBackend()
    backend.scroll("left")
    backend.scroll("right")
    assert backend.directions == ["left", "right"]


@pytest.mark.parametrize("direction", ["up", "down", ""])
def test_dry_run_backend_rejects_invalid_direction(direction):
    backend = DryRunLayoutScrollBackend()
    with pytest.raises(ValueError):
        backend.scroll(direction)


def test_umbriel_backend_sends_native_layout_scroll_action(monkeypatch):
    calls = []

    def fake_run(command, *, check, timeout):
        calls.append((command, check, timeout))

    monkeypatch.setattr(
        "aether.layout_scroll.backend.subprocess.run",
        fake_run,
    )
    backend = UmbrielLayoutScrollBackend()

    backend.scroll("left")
    backend.scroll("right")

    assert calls == [
        (["umbriel", "msg", "layout-scroll-left"], True, 2),
        (["umbriel", "msg", "layout-scroll-right"], True, 2),
    ]


def test_umbriel_backend_rejects_invalid_direction(monkeypatch):
    def unexpected_run(*args, **kwargs):
        pytest.fail("subprocess must not run for an invalid direction")

    monkeypatch.setattr(
        "aether.layout_scroll.backend.subprocess.run",
        unexpected_run,
    )
    with pytest.raises(ValueError):
        UmbrielLayoutScrollBackend().scroll("up")
