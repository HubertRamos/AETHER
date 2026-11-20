
from __future__ import annotations

import argparse
import time
from collections import deque

import cv2
import mediapipe as mp

from aether.activation.coordinator import ActivationCoordinator
from aether.actions import ActionPipeline
from aether.gestures.classifier import classify
from aether.gestures.engine import GestureEngine
from aether.gestures.tracker import HandTracker
from aether.gestures.types import Gesture
from aether.pointer import (
    DryRunPointerBackend,
    PointerController,
    PointerPipeline,
    PointerPosition,
)
from aether.vision.preview import MODEL, draw_hand


def gesture_name(gesture) -> str:
    return gesture.value.upper().replace("_", " ")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--camera", type=int, default=0)
    parser.add_argument("--width", type=int, default=640)
    parser.add_argument("--height", type=int, default=480)
    args = parser.parse_args()

    if not MODEL.exists():
        raise FileNotFoundError(f"Modelo ausente: {MODEL}")

    camera = cv2.VideoCapture(args.camera, cv2.CAP_V4L2)

    if not camera.isOpened():
        raise RuntimeError(
            f"Não foi possível abrir a câmera {args.camera}"
        )

    camera.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)

    options = mp.tasks.vision.HandLandmarkerOptions(
        base_options=mp.tasks.BaseOptions(
            model_asset_path=str(MODEL)
        ),
        running_mode=mp.tasks.vision.RunningMode.VIDEO,
        num_hands=2,
        min_hand_detection_confidence=0.5,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    tracker = HandTracker(release_after_frames=8)
    engine = GestureEngine()
    activation = ActivationCoordinator()
    pipeline = ActionPipeline()

    pointer_backend = DryRunPointerBackend()
    pointer_controller = PointerController(pointer_backend)
    pointer_pipeline = PointerPipeline(
        pointer_controller,
        pointer_hand="Right",
    )

    event_log = deque(maxlen=8)
    suppressed_hands: set[str] = set()

    start = time.monotonic()
    previous_timestamp = -1
    previous_frame_time = start

    fps_window = start
    frame_count = 0
    fps = 0.0

    try:
        with mp.tasks.vision.HandLandmarker.create_from_options(
            options
        ) as detector:

            while True:
                ok, frame = camera.read()

                if not ok:
                    print("Falha na captura da webcam.")
                    break

                now = time.monotonic()
                elapsed = now - previous_frame_time
                previous_frame_time = now

                frame = cv2.flip(frame, 1)

                height, width = frame.shape[:2]
                aspect_ratio = width / height

                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                image = mp.Image(
                    image_format=mp.ImageFormat.SRGB,
                    data=rgb,
                )

                timestamp = int((now - start) * 1000)
                timestamp = max(
                    timestamp,
                    previous_timestamp + 1,
                )
                previous_timestamp = timestamp

                result = detector.detect_for_video(
                    image, timestamp
                )

                detected = {}
                raw_status = {}
                pointer_positions = {}

                for index, landmarks in enumerate(
                    result.hand_landmarks
                ):
                    label = f"Hand {index + 1}"

                    if (
                        index < len(result.handedness)
                        and result.handedness[index]
                    ):
                        handedness = (
                            result.handedness[index][0].category_name
                        )

                        label = {
                            "Left": "Right",
                            "Right": "Left",
                        }.get(handedness, handedness)

                    raw_gesture = classify(
                        landmarks,
                        image_aspect_ratio=aspect_ratio,
                    )

                    detected[label] = raw_gesture
                    raw_status[label] = raw_gesture

                    pointer_positions[label] = PointerPosition(
                        max(0.0, min(1.0, float(landmarks[8].x))),
                        max(0.0, min(1.0, float(landmarks[8].y))),
                    )

                    draw_hand(frame, landmarks, label)

                # 1. Rastreamento.
                tracker.update(detected)
                visible = tracker.visible_gestures()

                # 2. Atualização da ativação.
                confirmed = activation.update(
                    visible,
                    elapsed,
                )

                if confirmed:
                    event_log.append(
                        "SYSTEM: ACTIVATION CONFIRMED"
                    )

                    suppressed_hands = {
                        hand
                        for hand, gesture in visible.items()
                        if gesture == Gesture.OPEN_PALM
                    }

                    engine.reset()

                # 3. Sincronização dos gestos.
                if not confirmed and suppressed_hands:
                    for hand in tuple(suppressed_hands):
                        hand_state = tracker.hands.get(hand)

                        if (
                            hand_state is None
                            or hand_state.gesture != Gesture.OPEN_PALM
                        ):
                            suppressed_hands.discard(hand)

                    if not suppressed_hands:
                        engine.reset()
                        gesture_events = engine.update(visible)
                    else:
                        gesture_events = []

                elif not confirmed:
                    gesture_events = engine.update(visible)

                else:
                    gesture_events = []

                # 4. Histórico de eventos de gesto.
                for event in gesture_events:
                    event_log.append(
                        f"{event.hand}: "
                        f"{event.event_type.value.upper()} "
                        f"({gesture_name(event.gesture)})"
                    )

                # 5. Pipeline de ações.
                enabled = (
                    activation.can_execute
                    and not confirmed
                )

                action_requests = pipeline.process(
                    gesture_events,
                    enabled=enabled,
                )

                # 6. Pipeline do ponteiro (DRY RUN).
                pointer_moved = pointer_pipeline.process(
                    pointer_positions,
                    visible,
                    enabled=enabled,
                    suppressed_hands=suppressed_hands,
                )

                # 7. Histórico de ações simuladas.
                for request in action_requests:
                    action_name = request.action.value.upper()

                    if request.event_type.value == "gesture_started":
                        message = (
                            f"{request.hand}: "
                            f"ACTION STARTED ({action_name})"
                        )

                    elif request.event_type.value == "gesture_changed":
                        previous = (
                            request.previous_action.value.upper()
                            if request.previous_action
                            else "NONE"
                        )

                        message = (
                            f"{request.hand}: "
                            f"{previous} -> {action_name}"
                        )

                    else:
                        message = (
                            f"{request.hand}: "
                            f"ACTION ENDED ({action_name})"
                        )

                    event_log.append(message)

                # 8. Métricas.
                frame_count += 1

                if now - fps_window >= 1.0:
                    fps = frame_count / (now - fps_window)
                    frame_count = 0
                    fps_window = now

                # Cabeçalho.
                cv2.putText(
                    frame,
                    "AETHER 1.2 | GESTURE SYNCHRONIZATION",
                    (15, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.60,
                    (255, 255, 255),
                    2,
                )

                cv2.putText(
                    frame,
                    f"FPS: {fps:.1f} | Hands: {len(visible)}",
                    (15, 58),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.50,
                    (190, 90, 255),
                    2,
                )

                # Estado de ativação.
                state = activation.state
                state_text = state.value.upper()

                state_color = {
                    "disabled": (150, 150, 150),
                    "arming": (0, 200, 255),
                    "active": (80, 255, 100),
                    "cooldown": (0, 100, 255),
                }.get(state.value, (255, 255, 255))

                cv2.putText(
                    frame,
                    f"ACTIVATION: {state_text}",
                    (15, 100),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.65,
                    state_color,
                    2,
                )

                if state.value in ("arming", "cooldown"):
                    remaining = activation.controller.remaining_time

                    cv2.putText(
                        frame,
                        f"TIME: {remaining:.1f}s",
                        (15, 130),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.50,
                        state_color,
                        2,
                    )

                # Estado individual das mãos.
                hand_offset = 165

                for index, (label, hand) in enumerate(
                    tracker.hands.items()
                ):
                    raw = raw_status.get(label)

                    raw_text = (
                        gesture_name(raw)
                        if raw is not None
                        else "NOT DETECTED"
                    )

                    visibility = (
                        "VISIBLE" if hand.visible else "MISSING"
                    )

                    status = (
                        f"{label}: {visibility} | "
                        f"RAW {raw_text} | "
                        f"STABLE {gesture_name(hand.gesture)}"
                    )

                    cv2.putText(
                        frame,
                        status,
                        (15, hand_offset + index * 25),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.42,
                        (100, 255, 150)
                        if hand.visible
                        else (120, 120, 120),
                        1,
                    )

                # Estado do ponteiro.
                pointer_y = 220
                last_position = (
                    pointer_backend.positions[-1]
                    if pointer_backend.positions
                    else None
                )

                pointer_active = (
                    pointer_moved and last_position is not None
                )

                pointer_status = (
                    "ACTIVE"
                    if pointer_active
                    else "INACTIVE"
                )

                pointer_color = (
                    (80, 255, 100)
                    if pointer_active
                    else (150, 150, 150)
                )

                cv2.putText(
                    frame,
                    f"POINTER (DRY RUN): {pointer_status}",
                    (15, pointer_y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.48,
                    pointer_color,
                    2,
                )

                if last_position is not None:
                    pointer_coordinates = (
                        f"X: {last_position.x:.3f} | "
                        f"Y: {last_position.y:.3f}"
                    )
                else:
                    pointer_coordinates = "X: -- | Y: --"

                cv2.putText(
                    frame,
                    pointer_coordinates,
                    (15, pointer_y + 25),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.42,
                    (220, 220, 220),
                    1,
                )

                # Intenções ativas.
                intent_y = 265

                cv2.putText(
                    frame,
                    "ACTIVE INTENTS",
                    (15, intent_y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.45,
                    (190, 90, 255),
                    2,
                )

                active_intents = (
                    pipeline.intent_manager.active_intents()
                )

                if active_intents:
                    for index, (hand, intent) in enumerate(
                        active_intents.items()
                    ):
                        cv2.putText(
                            frame,
                            f"{hand}: {intent.value.upper()}",
                            (15, intent_y + 23 + index * 20),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.42,
                            (80, 255, 100),
                            1,
                        )
                else:
                    cv2.putText(
                        frame,
                        "NONE",
                        (15, intent_y + 23),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.42,
                        (150, 150, 150),
                        1,
                    )

                # Ações simuladas ativas.
                action_y = 325

                cv2.putText(
                    frame,
                    "ACTIVE ACTIONS (DRY RUN)",
                    (15, action_y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.45,
                    (190, 90, 255),
                    2,
                )

                active_actions = pipeline.executor.active_actions()

                if active_actions:
                    for index, (hand, action) in enumerate(
                        active_actions.items()
                    ):
                        cv2.putText(
                            frame,
                            f"{hand}: {action.value.upper()}",
                            (15, action_y + 23 + index * 20),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.42,
                            (80, 255, 100),
                            1,
                        )
                else:
                    cv2.putText(
                        frame,
                        "NONE",
                        (15, action_y + 23),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.42,
                        (150, 150, 150),
                        1,
                    )

                # Histórico.
                log_y = 385

                cv2.putText(
                    frame,
                    "EVENT LOG",
                    (15, log_y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.45,
                    (190, 90, 255),
                    2,
                )

                for index, event_text in enumerate(event_log):
                    y = log_y + 23 + index * 18

                    if y >= height - 35:
                        break

                    cv2.putText(
                        frame,
                        event_text,
                        (15, y),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.37,
                        (255, 220, 120),
                        1,
                    )

                # Atalhos.
                cv2.putText(
                    frame,
                    "A: ARM | D: DEACTIVATE | ESC: EMERGENCY | Q: QUIT",
                    (15, height - 12),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.38,
                    (220, 220, 220),
                    1,
                )

                cv2.imshow(
                    "AETHER - Action Pipeline",
                    frame,
                )

                key = cv2.waitKey(1) & 0xFF

                if key == ord("a"):
                    pipeline.reset()
                    pointer_backend.reset()
                    engine.reset()
                    suppressed_hands.clear()

                    if activation.request_activation():
                        event_log.append(
                            "SYSTEM: ARMING REQUESTED"
                        )

                elif key == ord("d"):
                    activation.deactivate()
                    pipeline.reset()
                    pointer_backend.reset()
                    engine.reset()
                    suppressed_hands.clear()

                    event_log.append(
                        "SYSTEM: DEACTIVATION REQUESTED"
                    )

                elif key == 27:
                    activation.emergency_stop()
                    pipeline.reset()
                    pointer_backend.reset()
                    engine.reset()
                    suppressed_hands.clear()

                    event_log.append(
                        "SYSTEM: EMERGENCY STOP"
                    )

                elif key == ord("q"):
                    break

    finally:
        pipeline.reset()
        pointer_backend.reset()
        engine.reset()
        tracker.reset()
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
