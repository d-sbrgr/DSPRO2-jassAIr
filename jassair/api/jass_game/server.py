import asyncio
from contextlib import asynccontextmanager
from .camera import list_available_cameras, get_game_logic

available_cameras = []
main_event_loop = None
clients = []
log_clients = []
log_queue = asyncio.Queue()


async def broadcast_state():
    for client in clients:
        await client.send_json(get_game_logic().to_json())

async def broadcast_loop():
    while True:
        try:
            await broadcast_state()
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Error during broadcast_state: {e}")
        await asyncio.sleep(1)

async def broadcast_logs():
    while True:
        log = await log_queue.get()
        for ws in log_clients:
            try:
                await ws.send_json(log)
            except:
                pass

@asynccontextmanager
async def lifespan(app):
    get_available_cameras().clear()
    get_available_cameras().extend(list_available_cameras())
    set_main_event_loop(asyncio.get_running_loop())

    tasks = [
        asyncio.create_task(broadcast_loop()),
        asyncio.create_task(broadcast_logs())
    ]
    yield
    for task in tasks:
        task.cancel()
    try:
        await asyncio.gather(*tasks)
    except asyncio.CancelledError:
        pass


def get_main_event_loop():
    return main_event_loop

def get_available_cameras():
    return available_cameras

def set_main_event_loop(value):
    global main_event_loop
    main_event_loop = value

def get_log_queue():
    return log_queue

def get_clients():
    return clients

def get_log_clients():
    return log_clients
