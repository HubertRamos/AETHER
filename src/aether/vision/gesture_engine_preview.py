
from __future__ import annotations

import argparse
import time
from collections import deque

import cv2
import mediapipe as mp

from aether.gestures.classifier import classify
from aether.gestures.engine import GestureEngine
from aether.gestures.events import GestureEventType
from aether.gestures.tracker import HandTracker
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

    event_log = deque(maxlen=5)

    start = time.monotonic()
    previous_timestamp = -1

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

                frame = cv2.flip(frame, 1)

                height, width = frame.shape[:2]
                aspect_ratio = width / height

                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                image = mp.Image(
                    image_format=mp.ImageFormat.SRGB,
                    data=rgb,
                )

                timestamp = int(
                    (time.monotonic() - start) * 1000
                )
                timestamp = max(
                    timestamp, previous_timestamp + 1
                )
                previous_timestamp = timestamp

                result = detector.detect_for_video(
                    image, timestamp
                )

                detected = {}

                raw_status = {}

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

                    draw_hand(frame, landmarks, label)

                # Atualiza o rastreamento das mãos.
                tracker.update(detected)

                # Somente mãos visíveis podem gerar eventos.
                visible = tracker.visible_gestures()

                # Transforma os estados em eventos.
                events = engine.update(visible)

                for event in events:
                    event_log.append(
                        f"{event.hand}: "
                        f"{event.event_type.value.upper()} "
                        f"({gesture_name(event.gesture)})"
                    )

                frame_count += 1
                now = time.monotonic()

                if now - fps_window >= 1.0:
                    fps = frame_count / (now - fps_window)
                    frame_count = 0
                    fps_window = now

                cv2.putText(
                    frame,
                    "AETHER 0.4 | GESTURE ENGINE",
                    (15, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.65,
                    (255, 255, 255),
                    2,
                )

                cv2.putText(
                    frame,
                    f"FPS: {fps:.1f} | Hands: {len(result.hand_landmarks)}",
                    (15, 58),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (190, 90, 255),
                    2,
                )

                # Estado individual de cada mão.
                for index, (label, hand) in enumerate(
                    tracker.hands.items()
                ):
                    raw = raw_status.get(label)

                    raw_text = (
                        gesture_name(raw)
                        if raw is not None
                        else "NOT DETECTED"
                    )

                    stable_text = gesture_name(hand.gesture)

                    visibility = (
                        "VISIBLE" if hand.visible else "MISSING"
                    )

                    status = (
                        f"{label}: {visibility} | "
                        f"RAW {raw_text} | STABLE {stable_text}"
                    )

                    cv2.putText(
                        frame,
                        status,
                        (15, 95 + index * 28),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.45,
                        (100, 255, 150) if hand.visible else (120, 120, 120),
                        2,
                    )

                # Histórico recente de eventos.
                cv2.putText(
                    frame,
                    "EVENT LOG",
                    (15, 175),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (190, 90, 255),
                    2,
                )

                for index, event_text in enumerate(event_log):
                    cv2.putText(
                        frame,
                        event_text,
                        (15, 202 + index * 25),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.43,
                        (255, 220, 120),
                        1,
                    )

                cv2.imshow(
                    "AETHER - Gesture Engine",
                    frame,
                )

                if cv2.waitKey(1) & 0xFF == 27:
                    break

    finally:
        engine.reset()
        tracker.reset()
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
