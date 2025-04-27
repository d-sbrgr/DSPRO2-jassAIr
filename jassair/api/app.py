from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# In-memory game state
game_state = {
    "current_player": "NORTH",
    "current_trumpf": "Eichel",
    "current_trick": ["eichel_6", "schelle_ass"]
}

# Detection state (separate from game state)
detection_state = {
    "last_detected_card": "eichel_9",
    "detected_cards": ["rose_6", "rose_7", "rose_8", "rose_9", "rose_10"]
}

# Bot action state (separate from game state)
bot_state = {
    "last_agent_play": None
}

clients = []

class CorrectionRequest(BaseModel):
    correct_card: str

class CardUpdate(BaseModel):
    detected_card: str

class AgentPlayUpdate(BaseModel):
    played_card: str

@app.get("/", response_class=HTMLResponse)
async def root():
    with open("static/index.html") as f:
        return HTMLResponse(content=f.read())

@app.get("/state")
async def get_state():
    # In case frontend still wants initial load
    return JSONResponse(content={
        "game_state": game_state,
        "detection_state": detection_state,
        "bot_state": bot_state
    })

@app.post("/correction")
async def post_correction(correction: CorrectionRequest):
    detection_state["last_detected_card"] = correction.correct_card
    await broadcast_state()
    return {"status": "success", "new_card": correction.correct_card}

@app.post("/update_card")
async def update_card(card_update: CardUpdate):
    detection_state["last_detected_card"] = card_update.detected_card
    detection_state["detected_cards"].append(card_update.detected_card)
    await broadcast_state()
    return {"status": "card updated"}

@app.post("/update_agent_play")
async def update_agent_play(agent_update: AgentPlayUpdate):
    bot_state["last_agent_play"] = agent_update.played_card
    await broadcast_state()
    return {"status": "agent play updated"}

@app.post("/next_player")
async def next_player():
    player_order = ["NORTH", "EAST", "SOUTH", "WEST"]
    current_index = player_order.index(game_state["current_player"])
    game_state["current_player"] = player_order[(current_index + 1) % 4]
    await broadcast_state()
    return {"status": "next player set"}

@app.post("/push")
async def push_action():
    print("Push action triggered!")
    return {"status": "push action completed"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        await websocket.send_json(full_state())
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        clients.remove(websocket)

def full_state():
    return {
        "game_state": game_state,
        "detection_state": detection_state,
        "bot_state": bot_state
    }

async def broadcast_state():
    to_remove = []
    for client in clients:
        try:
            await client.send_json(full_state())
        except:
            to_remove.append(client)
    for client in to_remove:
        clients.remove(client)
