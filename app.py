import logging

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from requests import HTTPError

from jassair.api.jass_game.camera import gen_frames, get_game_logic
from jassair.api.jass_game.logging import setup_logger
from jassair.api.jass_game.server import get_log_clients, get_clients, get_available_cameras, lifespan

setup_logger()
logger = logging.getLogger("App")


class ResetGameRequest(BaseModel):
    dealer: str
    player: str


class TrumpActionRequest(BaseModel):
    action: str

app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def root():
    with open("static/index.html") as f:
        return HTMLResponse(content=f.read())

@app.get("/state")
async def get_state():
    state = get_game_logic().to_json()
    logger.info(f"get_state: {state}")
    return JSONResponse(content=state)

@app.put("/reset_game", status_code=204)
async def reset_game(req: ResetGameRequest):
    logger.info(f"reset_game: {req.dealer}, {req.player}")
    get_game_logic().reset(dealer=int(req.dealer), player=int(req.player))
    return

@app.put("/trump_action", status_code=204)
async def trump_action(req: TrumpActionRequest):
    logger.info(f"trump_action: {req.action}")
    get_game_logic().action(int(req.action))
    return

@app.get("/video_feed")
def video_feed(cam_index: int = 0):
    if cam_index not in get_available_cameras():
        raise HTTPError(status_code=400, detail="Invalid camera index")
    return StreamingResponse(gen_frames(cam_index), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/cameras")
async def get_cameras():
    return {"cameras": get_available_cameras()}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    get_clients().append(websocket)
    try:
        await websocket.send_json(get_game_logic().to_json())
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        get_clients().remove(websocket)

@app.websocket("/log")
async def log_stream(websocket: WebSocket):
    await websocket.accept()
    get_log_clients().append(websocket)
    try:
        while True:
            await websocket.receive_text()  # keep the connection open
    except WebSocketDisconnect:
        get_log_clients().remove(websocket)
