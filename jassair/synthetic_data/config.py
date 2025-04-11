from dataclasses import dataclass, field

from .image_augmentation import Augmentation


@dataclass
class SynthConfig:
    num_train: int = 10
    num_val: int = 0
    num_test: int = 0
    max_overlap: float = 0.1

    min_cards_per_image: int = 1
    max_cards_per_image: int = 9

    augment_background: list[Augmentation] = field(default_factory=list)
    augment_final: list[Augmentation] = field(default_factory=list)

    classes: list[int] = field(default_factory=list)
    backgrounds: list[int] = field(default_factory=list)