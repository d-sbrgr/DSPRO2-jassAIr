import logging

import cv2
from ultralytics import YOLO

from .color_utils import generate_distinct_colors
from .game_logic import GameLogic

logger = logging.getLogger("Camera")

model = YOLO(r"artifacts\yolov11-finetuned-model-non-overlapping-v0\best.pt")
CLASS_COLORS = generate_distinct_colors(36)

game_logic = GameLogic()

def list_available_cameras(max_tested=2):
    available = []
    for i in range(max_tested):
        try:
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if cap.read()[0]:
                available.append(i)
            cap.release()
        except:
            pass
    logger.info(f"Available cameras: {available}")
    return available

def gen_frames(cam_index=0):
    camera = cv2.VideoCapture(cam_index, cv2.CAP_DSHOW)
    try:
        while True:
            success, frame = camera.read()
            if not success:
                break
            results = model(frame, verbose=False)[0]
            active_cards = get_game_logic()(results)

            for result in results:
                if result.boxes.cls in active_cards:
                    confidence = float(result.boxes.conf)
                    cls = int(result.boxes.cls)
                    x1, y1, x2, y2 = result.boxes.xyxy.numpy()[0]
                    color = CLASS_COLORS[cls] if cls < len(CLASS_COLORS) else (255, 255, 255)
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                    cv2.putText(frame, f"{model.names[cls]} {confidence:.2f}",
                                (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    finally:
        camera.release()
        logger.info(f"Camera {cam_index} released.")


def get_game_logic():
    return game_logic
