import sys
from pathlib import Path
from enum import Enum, auto

ROOT = Path(__file__).parent.parent.parent

def get_data_path() -> Path:
    if sys.platform == 'win32': # Working locally on windows
        return ROOT / 'data'
    return Path("/exchange/dspro2/jassair") # Working on gpuhub (linux)


class Datasets(Enum):
    BACKGROUNDS = auto()
    CARD_TEMPLATE = auto()
    REAL_LIFE_BASELINE = auto()
    REAL_LIFE_YOLO = auto()
    S_1TO1_2CLASS_GREEN_B = auto()
    S_1TO1_2CLASS_MULT_B = auto()
    S_1TO1_10CLASS_MULT_B = auto()
    S_1TO2_20CLASS_MULT_B = auto()
    S_1TO2_36CLASS_MULT_B = auto()


def get_dataset_path(dataset: Datasets) -> Path:
    source_path = get_data_path()
    if dataset in Datasets:
        return source_path / dataset.name.lower()
    raise ValueError(f"Unknown dataset: {dataset}")
