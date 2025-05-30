import colorsys
import cv2

from contextlib import asynccontextmanager
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from game_logic import GameLogic

from ultralytics import YOLO

model = YOLO("../../artifacts/yolov11-finetuned-model-non-overlapping-v0/best.pt")
game_logic = GameLogic()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start background task
    broadcast_task = asyncio.create_task(broadcast_loop())

    yield  # App is running

    # Shutdown logic
    broadcast_task.cancel()
    try:
        await broadcast_task
    except asyncio.CancelledError:
        pass

app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")

clients = []

class CorrectionRequest(BaseModel):
    correct_card: str

class CardUpdate(BaseModel):
    detected_card: str

class AgentPlayUpdate(BaseModel):
    played_card: str


def list_available_cameras(max_tested=5):
    available = []
    for i in range(max_tested):
        cap = cv2.VideoCapture(i)
        if cap.read()[0]:
            available.append(i)
        cap.release()
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
        await broadcast_state()
        await asyncio.sleep(1)  # Send updates every 1 second (adjust as needed)

@app.get("/", response_class=HTMLResponse)
async def root():
    with open("static/index.html") as f:
        return HTMLResponse(content=f.read())

@app.get("/state")
async def get_state():
    state = game_logic.to_json()
    print("Returning state:", state)
    return JSONResponse(content=state)

@app.post("/update_card")
async def update_card(card_update: CardUpdate):
    #detection_state["detected_cards"].append(card_update.detected_card)
    await broadcast_state()
    return {"status": "card updated"}

@app.post("/update_agent_play")
async def update_agent_play(agent_update: AgentPlayUpdate):
    #bot_state["last_agent_play"] = agent_update.played_card
    await broadcast_state()
    return {"status": "agent play updated"}

@app.post("/next_player")
async def next_player():
    #player_order = ["NORTH", "EAST", "SOUTH", "WEST"]
    #current_index = player_order.index(game_state["current_player"])
    #game_state["current_player"] = player_order[(current_index + 1) % 4]
    await broadcast_state()
    return {"status": "next player set"}

@app.post("/push")
async def push_action():
    print("Push action triggered!")
    return {"status": "push action completed"}


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
        try:
            await client.send_json(game_logic.to_json())
        except:
            to_remove.append(client)
    for client in to_remove:
        clients.remove(client)
