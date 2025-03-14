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


def get_dataset_path(dataset: Datasets) -> Path:
    source_path = get_data_path()
    if dataset == Datasets.SWISS:
        return source_path / 'swiss-cards'
    if dataset == Datasets.FRENCH:
        return source_path / 'french-cards'
    raise ValueError(f"Unknown dataset: {dataset}")
