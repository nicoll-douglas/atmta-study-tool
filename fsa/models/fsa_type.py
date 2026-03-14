from enum import IntFlag, auto


class FSAType(IntFlag):
    """Represents the type of an FSA using bitwise flags."""

    DFA = auto()
    COMPLETE = auto()
    NFA = auto()
    EPSILON_NFA = auto()
