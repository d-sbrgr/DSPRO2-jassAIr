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
    R_1TO1_36C_NOVLP = auto()
    R_1TO9_36C_NOVLP = auto()
    S_1TO1_36C_NOVLP = auto()
    S_1TO9_36C_NOVLP = auto()
    S_1TO9_36C_OVLP = auto()
    SRF_1TO9_36C_MOVLP = auto()


def get_dataset_path(dataset: Datasets) -> Path:
    source_path = get_data_path()
    if dataset in Datasets:
        return source_path / dataset.name.lower()
    raise ValueError(f"Unknown dataset: {dataset}")
