import logging
from itertools import cycle

from ultralytics.engine.results import Results

logger = logging.getLogger("Detection")


class CardState:
    def __init__(self, window_size: int = 15, presence_threshold: int = 12):
        if window_size < presence_threshold:
            raise ValueError("Window size must be greater than or equal to presence_threshold")
        self._presence_threshold = presence_threshold
        self._rolling_window = [False] * window_size
        self._index = cycle(range(window_size))

    def reset(self):
        self._rolling_window = [False] * len(self._rolling_window)

    @property
    def is_active(self) -> bool:
        return sum(self._rolling_window) > self._presence_threshold

    def __call__(self, is_present: bool) -> bool:
        index = next(self._index)
        self._rolling_window[index] = is_present
        return sum(self._rolling_window) >= self._presence_threshold


class DetectionState:
    def __init__(self, *, conf_threshold: float = 0.7, num_cards: int = 36):
        self._conf_threshold = conf_threshold
        self._cards = [CardState() for _ in range(num_cards)]
        self._detected_cards = [False for _ in range(num_cards)]
        self._num_cards = num_cards

    def reset(self):
        logger.info("Reset")
        for card in self._cards:
            card.reset()
        self._detected_cards = [False for _ in range(self._num_cards)]

    def correct_detection(self, old_card_index: int, new_card_index: int):
        logger.info(f"Correction: {old_card_index} -> {new_card_index}")
        self._detected_cards[old_card_index] = False
        self._detected_cards[new_card_index] = True

    def get_active_detections(self, results: Results) -> list[int]:
        result = []
        for r in results:
            if self._cards[int(r.boxes.cls)].is_active:
                result.append(int(r.boxes.cls))
        logger.debug(f"Active detections: {result}")
        return result

    def __call__(self, results: Results) -> tuple[int, ...]:
        logger.debug("Detection call")
        detections = []
        for index in range(self._num_cards):
            is_present = False
            if index in results.boxes.cls:
                t_index = int((results.boxes.cls == index).nonzero()[0])
                if float(results.boxes.conf[t_index]) >= self._conf_threshold:
                    is_present = True
            if self._cards[index](is_present):
                if not self._detected_cards[index]:
                    detections.append(index)
                    logger.info(f"Detected card {index}")
                    self._detected_cards[index] = True
        return tuple(detections)
