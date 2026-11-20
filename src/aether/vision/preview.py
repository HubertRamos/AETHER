from __future__ import annotations

import argparse
import time
from pathlib import Path

import cv2
import mediapipe as mp


ROOT = Path(__file__).resolve().parents[3]
MODEL = ROOT / "assets" / "models" / "hand_landmarker.task"

CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20),
    (0, 17),
]


def draw_hand(frame, landmarks, label):
    height, width = frame.shape[:2]

    points = [
        (int(point.x * width), int(point.y * height))
        for point in landmarks
    ]

    for start, end in CONNECTIONS:
        cv2.line(
            frame, points[start], points[end],
            (190, 90, 255), 2
        )

    for x, y in points:
        cv2.circle(
            frame, (x, y), 4,
            (255, 255, 255), -1
        )

    wrist_x, wrist_y = points[0]

    cv2.putText(
        frame, label,
        (wrist_x, max(25, wrist_y - 15)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6, (190, 90, 255), 2
    )


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

                hands = len(result.hand_landmarks)

                for index, landmarks in enumerate(
                    result.hand_landmarks
                ):
                    label = f"Hand {index + 1}"

                    if index < len(result.handedness):
                        categories = result.handedness[index]
                        if categories:
                            label = categories[0].category_name

                    draw_hand(frame, landmarks, label)

                frame_count += 1
                now = time.monotonic()

                if now - fps_window >= 1.0:
                    fps = frame_count / (now - fps_window)
                    frame_count = 0
                    fps_window = now

                cv2.putText(
                    frame,
                    f"AETHER 0.1 | Hands: {hands}",
                    (15, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.65, (255, 255, 255), 2
                )

                cv2.putText(
                    frame,
                    f"FPS: {fps:.1f}",
                    (15, 58),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55, (190, 90, 255), 2
                )

                cv2.imshow("AETHER - Vision", frame)

                if cv2.waitKey(1) & 0xFF == 27:
                    break

    finally:
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()