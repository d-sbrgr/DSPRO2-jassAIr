from typing import Any

from .jass_game.game_state import GameState
from .jass_game.detection_state import DetectionState

# game_state = {
#     "current_player": "NORTH",
#     "current_trumpf": "Eichel",
#     "current_trick": ["eichel_6", "schelle_ass"]
# }
#
# # Detection state (separate from game state)
# detection_state = {
#     "last_detected_card": "eichel_9",
#     "detected_cards": ["rose_6", "rose_7", "rose_8", "rose_9", "rose_10"]
# }
#
# # Bot action state (separate from game state)
# bot_state = {
#     "last_agent_play": None
# }

class GameLogic:
    def __init__(self):
        self._game_state = GameState()
        self._detection_state = DetectionState()

    def get_game_state(self) -> dict[str, Any]:
        pass

    def get_detection_state(self) -> dict[str, Any]:
        pass

    def get_bot_state(self) -> dict[str, Any]:
        pass