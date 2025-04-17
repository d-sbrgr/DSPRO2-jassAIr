from enum import IntEnum

class CardClass(IntEnum):
    EICHEL_10 = 0
    EICHEL_6 = 1
    EICHEL_7 = 2
    EICHEL_8 = 3
    EICHEL_9 = 4
    EICHEL_ASS = 5
    EICHEL_KONIG = 6
    EICHEL_OBER = 7
    EICHEL_UNDER = 8
    ROSE_10 = 9
    ROSE_6 = 10
    ROSE_7 = 11
    ROSE_8 = 12
    ROSE_9 = 13
    ROSE_ASS = 14
    ROSE_KONIG = 15
    ROSE_OBER = 16
    ROSE_UNDER = 17
    SCHELLE_10 = 18
    SCHELLE_6 = 19
    SCHELLE_7 = 20
    SCHELLE_8 = 21
    SCHELLE_9 = 22
    SCHELLE_ASS = 23
    SCHELLE_KONIG = 24
    SCHELLE_OBER = 25
    SCHELLE_UNDER = 26
    SCHILTE_10 = 27
    SCHILTE_6 = 28
    SCHILTE_7 = 29
    SCHILTE_8 = 30
    SCHILTE_9 = 31
    SCHILTE_ASS = 32
    SCHILTE_KONIG = 33
    SCHILTE_OBER = 34
    SCHILTE_UNDER = 35


def get_class_for_name(name: str) -> CardClass:
    """Returns the class index for a given card name.

    Card names must be in input format {suit}_{rank}.

    Examples:
        "rose_10"
        "schilte_under"
        "eichel_6"

    :param name: Name of the given card class
    :return: Integer index of the given card class
    """
    return getattr(CardClass, name.upper())
