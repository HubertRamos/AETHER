
import pytest

from aether.actions import Action, ActionPipeline, DryRunBackend
from aether.gestures.events import GestureEvent, GestureEventType
from aether.gestures.types import Gesture


def make_event(
    gesture=Gesture.POINT,
    event_type=GestureEventType.GESTURE_STARTED,
    hand="Right",
):
    return GestureEvent(
        event_type=event_type,
        hand=hand,
        gesture=gesture,
    )


def create_pipeline():
    backend = DryRunBackend()
    pipeline = ActionPipeline(backend)
    return pipeline, backend


def test_pipeline_processes_gesture_start():
    pipeline, backend = create_pipeline()

    result = pipeline.process([make_event()], enabled=True)

    assert len(result) == 1
    assert result[0].action == Action.POINTER
    assert len(backend.records) == 1


def test_pipeline_processes_gesture_change():
    pipeline, backend = create_pipeline()

    pipeline.process([make_event()], enabled=True)

    result = pipeline.process(
        [
            make_event(
                gesture=Gesture.PINCH,
                event_type=GestureEventType.GESTURE_CHANGED,
            )
        ],
        enabled=True,
    )

    assert len(result) == 1
    assert result[0].action == Action.SELECT
    assert result[0].previous_action == Action.POINTER


def test_pipeline_processes_gesture_end():
    pipeline, backend = create_pipeline()

    pipeline.process([make_event()], enabled=True)

    result = pipeline.process(
        [
            make_event(
                event_type=GestureEventType.GESTURE_ENDED,
            )
        ],
        enabled=True,
    )

    assert len(result) == 1
    assert result[0].event_type == GestureEventType.GESTURE_ENDED
    assert pipeline.executor.active_actions() == {}


def test_pipeline_supports_two_hands():
    pipeline, backend = create_pipeline()

    result = pipeline.process(
        [
            make_event(hand="Right"),
            make_event(
                gesture=Gesture.PINCH,
                hand="Left",
            ),
        ],
        enabled=True,
    )

    assert len(result) == 2

    assert pipeline.executor.active_actions() == {
        "Right": Action.POINTER,
        "Left": Action.SELECT,
    }


def test_pipeline_ignores_unknown_gesture():
    pipeline, backend = create_pipeline()

    result = pipeline.process(
        [make_event(gesture=Gesture.UNKNOWN)],
        enabled=True,
    )

    assert result == ()
    assert backend.records == []


def test_pipeline_reset_releases_actions():
    pipeline, backend = create_pipeline()

    pipeline.process([make_event()], enabled=True)

    result = pipeline.reset()

    assert len(result) == 1
    assert result[0].event_type == GestureEventType.GESTURE_ENDED
    assert pipeline.executor.active_actions() == {}


def test_disabling_pipeline_releases_actions():
    pipeline, backend = create_pipeline()

    pipeline.process([make_event()], enabled=True)

    result = pipeline.process([], enabled=False)

    assert len(result) == 1
    assert pipeline.executor.active_actions() == {}


def test_disabled_pipeline_does_not_execute_events():
    pipeline, backend = create_pipeline()

    result = pipeline.process([make_event()], enabled=False)

    assert result == ()
    assert backend.records == []


def test_pipeline_accepts_empty_events():
    pipeline, backend = create_pipeline()

    result = pipeline.process([], enabled=True)

    assert result == ()
    assert backend.records == []


def test_pipeline_rejects_invalid_events():
    pipeline, backend = create_pipeline()

    with pytest.raises(TypeError):
        pipeline.process("invalid", enabled=True)


def test_pipeline_rejects_invalid_enabled():
    pipeline, backend = create_pipeline()

    with pytest.raises(TypeError):
        pipeline.process([], enabled=1)
