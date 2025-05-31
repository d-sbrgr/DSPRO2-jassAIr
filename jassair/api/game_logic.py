import logging
from typing import Any

from jass.game.const import TRUMP_FULL_P
from ultralytics.engine.results import Results

from jass_game.detection_state import DetectionState
from jass_game.game_state import GameState

logger = logging.getLogger("GameLogic")

PLAYERS = ["NORTH (1)", "EAST (2)", "SOUTH (3)", "WEST (4)", "N/A"]
TRUMPS = ["Schelle", "Rose", "Schilte", "Eichel", "Obe Abe", "Une Ufe", "N/A"]


class GameLogic:
    _static_names = ["schelle_trumpf", "rose_trumpf", "schilte_trumpf", "eichel_trumpf", "obe_abe", "une_ufe", "schiebe"]
    def __init__(self):
        self._game_state = GameState()
        self._detection_state = DetectionState()
        self._card_names = None
        self._detected_cards = []

    def get_game_state(self) -> dict[str, Any]:
        state = self._game_state.state
        if not state:
            return {
                "current_player": "N/A",
                "current_trumpf": "N/A",
                "current_trick": []
            }
        current_trick = []
        if self._card_names:
            current_trick = [self._card_names[card] for card in self._game_state.current_trick]
        return {
            "current_player": PLAYERS[state.player],
            "current_trumpf": TRUMPS[state.trump],
            "current_trick": current_trick,
        }

    def get_detection_state(self) -> dict[str, Any]:
        cards = []
        if self._card_names:
            cards = [self._card_names[i] for i in self._detected_cards]
        return {
            "detected_cards": cards
        }

    def get_bot_state(self) -> dict[str, Any]:
        agent_play = self._game_state.last_agent_play
        if agent_play and self._card_names:
            agent_play = self._card_names[agent_play]
        return {
            "last_agent_play": agent_play
        }

    def to_json(self):
        return {
            "game_state": self.get_game_state(),
            "detection_state": self.get_detection_state(),
            "bot_state": self.get_bot_state()
        }

    def action(self, action: int):
        if not self._game_state.state:
            logger.warning(f"Action: {action} - game not started")
        elif action > 35 and not self._game_state.state.trump == -1:
            logger.warning(f"Action: {action} - trump already selected")
        elif action == TRUMP_FULL_P and not self._game_state.state.forehand == -1:
            logger.warning(f"Action: {action} - already pushed")
        else:
            self._game_state.action(action)

    def reset(self, dealer: int, player: int):
        self._game_state.reset(dealer, player)
        self._detection_state.reset()
        self._detected_cards.clear()
        self._card_names = None

    def __call__(self, results: Results) -> list[int]:
        if self._card_names is None:
            self._card_names = [name.lower().replace(" ", "_") for name in results.names.values()]
            self._card_names.extend(self._static_names)
        new_detections = self._detection_state(results)
        for detection in new_detections:
            self.action(detection)
        self._detected_cards.extend(new_detections)
        active_detections = self._detection_state.get_active_detections(results)
        return active_detections