import logging
import asyncio

from .server import get_main_event_loop, get_log_queue

class WebSocketLogHandler(logging.Handler):
    def emit(self, record):
        if get_main_event_loop() is None:
            return
        msg = self.format(record)
        try:
            asyncio.run_coroutine_threadsafe(
                get_log_queue().put({"level": record.levelname, "message": msg}),
                get_main_event_loop()
            )
        except Exception:
            pass

def setup_logger():
    handler = WebSocketLogHandler()
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)
