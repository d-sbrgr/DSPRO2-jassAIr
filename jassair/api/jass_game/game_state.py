import numpy as np
import requests

from jass.game.const import card_ids, TRUMP_FULL_OFFSET
from jass.service.player_service_route import PLAY_CARD_PATH_PREFIX, SELECT_TRUMP_PATH_PREFIX
from jass.game.game_state import GameState as JassGameState
from jass.game.game_sim import GameSim
from jass.game.game_rule import GameRule
from jass.game.rule_schieber import RuleSchieber


YOLO_2_JASS = np.array([
    31,
    35,
    34,
    33,
    32,
    27,
    28,
    29,
    30,
    13,
    17,
    16,
    15,
    14,
    9,
    10,
    11,
    12,
    4,
    8,
    7,
    6,
    5,
    0,
    1,
    2,
    3,
    22,
    26,
    25,
    24,
    23,
    18,
    19,
    20,
    21,
    36,
    37,
    38,
    39,
    40,
    41,
    42,
    43,
])


class GameState:
    rule: GameRule = RuleSchieber()
    timeout: int = 10.0

    def __init__(self, url: str = "https://jassair-470541508978.europe-west1.run.app/jassager"):
        self._player_cards: list[int] = []
        self._sim: GameSim | None = None
        self._dealer: int | None = None
        self._player: int | None = None
        self._player_action: int | None = None
        self._url = url

    @property
    def state(self) -> JassGameState | None:
        if self._sim:
            return self._sim.state
        return None

    def action(self, card: int):
        if len(self._player_cards) < 9:
            self._player_cards.append(YOLO_2_JASS[card])
            if len(self._player_cards) == 9:
                hands =  np.zeros(shape=[4, 36], dtype=np.int32)
                hands[self._player][self._player_cards] = 1
                self._sim.init_from_cards(hands, self._dealer)
                self.get_bot_move()
        else:
            action = YOLO_2_JASS[card]
            self._sim.action(action)
            self.get_bot_move()

    def get_bot_move(self):
        if self._sim.state.player == self._player:
            data = self._sim.get_observation().to_json()
            if self._sim.state.trump == -1:
                response = requests.post(self._url + SELECT_TRUMP_PATH_PREFIX, json=data, timeout=self.timeout)
                response_data = response.json()
                action = int(response_data['trump']) + TRUMP_FULL_OFFSET
            else:
                response = requests.post(self._url + PLAY_CARD_PATH_PREFIX, json=data, timeout=self.timeout)
                response_data = response.json()
                card = response_data['card']
                action = card_ids[card]
            self._player_action = int((YOLO_2_JASS == 12).nonzero()[0][0])
            self.action(action)

    def reset(self, dealer: int, player: int):
        self._player_cards.clear()
        self._sim = GameSim(self.rule)
        self._dealer = dealer
        self._player = player
