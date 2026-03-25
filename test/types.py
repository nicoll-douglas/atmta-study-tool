from fsa.models.state import State
from language.models.word import Word
from language.models.symbol import Symbol
from typing import Literal

type TransitionCountData = tuple[
    dict[
        State, dict[Literal["incoming", "outgoing", "loop"], int]
    ],  # incoming, outgoing, loop transition counts for a state
    dict[Symbol | Word, int],  # transition counts for a symbol
]
