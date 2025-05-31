import asyncio
import colorsys
import logging
from contextlib import asynccontextmanager

import cv2
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from ultralytics import YOLO

from game_logic import GameLogic

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(name)s - %(message)s')
logger = logging.getLogger("App")
model = YOLO("../../artifacts/yolov11-finetuned-model-non-overlapping-v0/best.pt")
game_logic = GameLogic()


class ResetGameRequest(BaseModel):
    dealer: str
    player: str


class TrumpActionRequest(BaseModel):
    action: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    broadcast_task = asyncio.create_task(broadcast_loop())
    yield
    broadcast_task.cancel()
    try:
        await broadcast_task
    except asyncio.CancelledError:
        pass

app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")

clients = []


def list_available_cameras(max_tested=2):
    available = []
    for i in range(max_tested):
        cap = cv2.VideoCapture(i)
        if cap.read()[0]:
            available.append(i)
        cap.release()
    logger.info(f"Available cameras: {available}")
    return available

def generate_distinct_colors(n):
    """Generate `n` distinct, visually distinguishable colors in BGR format."""
    hsv_colors = [(i / n, 1.0, 1.0) for i in range(n)]
    rgb_colors = [tuple(int(c * 255) for c in colorsys.hsv_to_rgb(*hsv)) for hsv in hsv_colors]
    bgr_colors = [tuple(reversed(rgb)) for rgb in rgb_colors]
    return bgr_colors


CLASS_COLORS = generate_distinct_colors(36)


def gen_frames(cam_index=0):
    camera = cv2.VideoCapture(cam_index)
    while True:
        success, frame = camera.read()
        if not success:
            break

        results = model(frame, verbose=False)[0]
        active_cards = game_logic(results)

        for result in results:
            if result.boxes.cls in active_cards:
                confidence = float(result.boxes.conf)
                cls = int(result.boxes.cls)
                x1, y1, x2, y2 = result.boxes.xyxy.numpy()[0]

                # Get color from list, fallback to white if out of bounds
                color = CLASS_COLORS[cls] if cls < len(CLASS_COLORS) else (255, 255, 255)

                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                cv2.putText(frame, f"{model.names[cls]} {confidence:.2f}", (int(x1), int(y1) - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


async def broadcast_loop():
    while True:
        try:
            await broadcast_state()
        except Exception as e:
            logger.error(f"Error during broadcast_state: {e}")
        await asyncio.sleep(1)

@app.get("/", response_class=HTMLResponse)
async def root():
    with open("static/index.html") as f:
        return HTMLResponse(content=f.read())

@app.get("/state")
async def get_state():
    state = game_logic.to_json()
    logger.info(f"get_state: {state}")
    return JSONResponse(content=state)

@app.put("/reset_game", status_code=204)
async def reset_game(req: ResetGameRequest):
    logger.info(f"reset_game: {req.dealer}, {req.player}")
    game_logic.reset(dealer=int(req.dealer), player=int(req.player))
    return

@app.put("/trump_action", status_code=204)
async def trump_action(req: TrumpActionRequest):
    logger.info(f"trump_action: {req.action}")
    game_logic.action(int(req.action))
    return

@app.get("/video_feed")
def video_feed(cam_index: int = 0):
    return StreamingResponse(gen_frames(cam_index), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/cameras")
async def get_cameras():
    return {"cameras": list_available_cameras()}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        await websocket.send_json(game_logic.to_json())
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        clients.remove(websocket)

async def broadcast_state():
    to_remove = []
    for client in clients:
        await client.send_json(game_logic.to_json())
