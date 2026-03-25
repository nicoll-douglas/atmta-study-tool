from atmta_study_tool.fsa.models import State
from atmta_study_tool.language.models import Word, Symbol
from typing import Literal

type TransitionCountData = tuple[
    dict[
        State, dict[Literal["incoming", "outgoing", "loop"], int]
    ],  # incoming, outgoing, loop transition counts for a state
    dict[Symbol | Word, int],  # transition counts for a symbol
]
