import sys
from pathlib import Path
from enum import Enum, auto

ROOT = Path(__file__).parent.parent.parent

def get_data_path() -> Path:
    if sys.platform == 'win32': # Working locally on windows
        return ROOT / 'data'
    return Path("/exchange/dspro2/jassair") # Working on gpuhub (linux)


class Datasets(Enum):
    SWISS = auto()
    FRENCH = auto()
    BACKGROUNDS = auto()
    SYNTHETIC_SINGLE = auto()
    SYNTHETIC_MULTIPLE = auto()
    REAL_LIFE_TEST = auto()
    REAL_LIFE_YOLO = auto()


def get_dataset_path(dataset: Datasets) -> Path:
    source_path = get_data_path()
    match dataset:
        case Datasets.SWISS:
            return source_path / 'swiss-cards'
        case Datasets.FRENCH:
            return source_path / 'french-cards'
        case Datasets.BACKGROUNDS:
            return source_path / 'backgrounds'
        case Datasets.SYNTHETIC_SINGLE:
            return source_path / 'synth_single'
        case Datasets.SYNTHETIC_MULTIPLE:
            return source_path / 'synth_multiple'
        case Datasets.REAL_LIFE_TEST:
            return source_path / 'real_life_test'
        case Datasets.REAL_LIFE_YOLO:
            return source_path / 'real_life_yolo'
        case _:
            raise ValueError(f"Unknown dataset: {dataset}")
