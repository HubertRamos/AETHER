from unittest.mock import Mock

import pytest

from aether.click.backend import DryRunClickBackend, YdotoolClickBackend


def test_dry_run_backend_records_click_counts():
    backend = DryRunClickBackend()
    backend.click()
    backend.click(count=2)
    assert backend.clicks == [1, 2]


def test_ydotool_backend_executes_left_clicks(monkeypatch):
    run = Mock()
    monkeypatch.setattr("aether.click.backend.subprocess.run", run)
    YdotoolClickBackend().click(count=2)
    assert run.call_count == 2
    run.assert_called_with(["ydotool", "click", "0xC0"], check=True, timeout=2)


def test_backend_rejects_invalid_count():
    with pytest.raises(ValueError):
        DryRunClickBackend().click(count=3)


def test_ydotool_backend_executes_right_click(monkeypatch):
    run = Mock()
    monkeypatch.setattr("aether.click.backend.subprocess.run", run)
    YdotoolClickBackend().click(button="right")
    run.assert_called_once_with(["ydotool", "click", "0xC1"], check=True, timeout=2)


def test_dry_run_backend_records_button():
    backend = DryRunClickBackend()
    backend.click(button="right")
    assert backend.clicks == [1]
    assert backend.buttons == ["right"]


@pytest.mark.parametrize(("method", "code", "button"), [
    ("press", "0x40", "left"),
    ("release", "0x80", "left"),
    ("press", "0x41", "right"),
    ("release", "0x81", "right"),
])
def test_ydotool_backend_holds_and_releases(monkeypatch, method, code, button):
    run = Mock()
    monkeypatch.setattr("aether.click.backend.subprocess.run", run)
    getattr(YdotoolClickBackend(), method)(button=button)
    run.assert_called_once_with(["ydotool", "click", code], check=True, timeout=2)
