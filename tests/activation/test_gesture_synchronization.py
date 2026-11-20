
from aether.gestures.types import Gesture


def test_activation_confirmation_gesture_does_not_start_action():
    """
    O gesto OPEN_PALM usado para confirmar a ativação
    não pode iniciar uma ação PAUSE.
    """
    from aether.actions import ActionPipeline
    from aether.gestures.engine import GestureEngine

    engine = GestureEngine()
    pipeline = ActionPipeline()

    # Simula a palma aberta usada na confirmação.
    confirmation_gesture = {
        "Hand 1": Gesture.OPEN_PALM,
    }

    # O gesto pode ser detectado pelo engine,
    # mas não deve chegar à pipeline como ação.
    events = engine.update(confirmation_gesture)

    requests = pipeline.process(
        events,
        enabled=False,
    )

    assert requests == ()
    assert pipeline.intent_manager.active_intents() == {}
    assert pipeline.executor.active_actions() == {}


def test_first_gesture_after_confirmation_starts_normally():
    """
    Depois de liberar o gesto de confirmação,
    um novo POINT deve iniciar POINTER.
    """
    from aether.actions import Action, ActionPipeline
    from aether.gestures.engine import GestureEngine

    engine = GestureEngine()
    pipeline = ActionPipeline()

    # Estado inicial: gesto de confirmação.
    engine.update({
        "Hand 1": Gesture.OPEN_PALM,
    })

    # Simula a liberação da mão/gesto de confirmação.
    engine.reset()

    # Novo gesto após a ativação.
    events = engine.update({
        "Hand 1": Gesture.POINT,
    })

    requests = pipeline.process(
        events,
        enabled=True,
    )

    assert len(requests) == 1
    assert requests[0].action == Action.POINTER
    assert pipeline.intent_manager.active_intents()["Hand 1"].value == "point"
    assert pipeline.executor.active_actions()["Hand 1"] == Action.POINTER


def test_held_gesture_does_not_generate_repeated_actions():
    """
    Manter o mesmo gesto por vários frames não deve
    gerar novos eventos ou ações repetidas.
    """
    from aether.actions import Action, ActionPipeline
    from aether.gestures.engine import GestureEngine

    engine = GestureEngine()
    pipeline = ActionPipeline()

    hand = {"Hand 1": Gesture.POINT}

    # Primeiro frame: inicia o gesto.
    events = engine.update(hand)

    requests = pipeline.process(
        events,
        enabled=True,
    )

    assert len(requests) == 1
    assert requests[0].action == Action.POINTER

    # Frames seguintes: mantém o mesmo gesto.
    for _ in range(20):
        events = engine.update(hand)

        requests = pipeline.process(
            events,
            enabled=True,
        )

        assert requests == ()

    # A ação continua ativa, sem duplicações.
    assert pipeline.executor.active_actions() == {
        "Hand 1": Action.POINTER
    }


def test_two_hands_keep_actions_independent():
    from aether.actions import Action, ActionPipeline
    from aether.gestures.engine import GestureEngine

    engine = GestureEngine()
    pipeline = ActionPipeline()

    events = engine.update({
        "Hand 1": Gesture.POINT,
        "Hand 2": Gesture.TWO_FINGERS,
    })

    requests = pipeline.process(
        events,
        enabled=True,
    )

    assert len(requests) == 2

    assert pipeline.executor.active_actions() == {
        "Hand 1": Action.POINTER,
        "Hand 2": Action.SECONDARY,
    }


def test_deactivation_releases_all_active_actions():
    from aether.actions import Action, ActionPipeline
    from aether.gestures.engine import GestureEngine

    engine = GestureEngine()
    pipeline = ActionPipeline()

    events = engine.update({
        "Hand 1": Gesture.POINT,
        "Hand 2": Gesture.TWO_FINGERS,
    })

    pipeline.process(events, enabled=True)

    assert len(pipeline.executor.active_actions()) == 2

    # Simula a desativação do sistema.
    requests = pipeline.reset()

    assert pipeline.intent_manager.active_intents() == {}
    assert pipeline.executor.active_actions() == {}

    assert len(requests) == 2
    assert all(
        request.event_type.value == "gesture_ended"
        for request in requests
    )


def test_emergency_stop_releases_all_active_actions():
    from aether.actions import Action, ActionPipeline
    from aether.gestures.engine import GestureEngine

    engine = GestureEngine()
    pipeline = ActionPipeline()

    events = engine.update({
        "Hand 1": Gesture.POINT,
        "Hand 2": Gesture.TWO_FINGERS,
    })

    pipeline.process(events, enabled=True)

    assert len(pipeline.executor.active_actions()) == 2

    # Simula a interrupção de emergência.
    requests = pipeline.reset()

    assert pipeline.executor.active_actions() == {}
    assert pipeline.intent_manager.active_intents() == {}

    assert len(requests) == 2
    assert all(
        request.event_type.value == "gesture_ended"
        for request in requests
    )


def test_emergency_stop_interrupts_activation():
    from aether.activation.coordinator import ActivationCoordinator
    from aether.activation.states import ActivationState

    activation = ActivationCoordinator()

    # Inicia o processo de ativação.
    assert activation.request_activation() is True
    assert activation.state == ActivationState.ARMING

    # Interrupção de emergência.
    activation.emergency_stop()

    assert activation.state == ActivationState.COOLDOWN
    assert activation.can_execute is False
