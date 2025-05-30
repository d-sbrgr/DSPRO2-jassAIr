from typing import Any

from ultralytics.engine.results import Results
from jass_game.game_state import GameState
from jass_game.detection_state import DetectionState


class GameLogic:
    def __init__(self):
        self._game_state = GameState()
        self._detection_state = DetectionState()
        self._card_names = None
        self._detected_cards = []


    def get_game_state(self) -> dict[str, Any]:
        return {
            "current_player": "NORTH",
            "current_trumpf": "Eichel",
            "current_trick": ["eichel_6", "schelle_ass"]
        }

    def get_detection_state(self) -> dict[str, Any]:
        return {
            "detected_cards": [self._card_names[i] for i in self._detected_cards]
        }

    def get_bot_state(self) -> dict[str, Any]:

        return {
            "last_agent_play": None
        }

    def to_json(self):
        return {
            "game_state": self.get_game_state(),
            "detection_state": self.get_detection_state(),
            "bot_state": self.get_bot_state()
        }

    def __call__(self, results: Results) -> list[int]:
        if self._card_names is None:
            self._card_names = [name.lower().replace(" ", "_") for name in results.names.values()]
        self._detected_cards.extend(self._detection_state(results))
        active_detections = self._detection_state.get_active_detections(results)
        return active_detections