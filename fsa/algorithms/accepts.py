from typing import TYPE_CHECKING
from ..models.fsa_type import FSAType
from .subset_construction import subset_construction

if TYPE_CHECKING:
    from ..models.fsa import FSA
    from ..models.state import State


def _dfa_accepts(dfa: FSA, word: str) -> bool:
    """Return True if the given DFA accepts the given word,
    otherwise False.

    Raises:
        ValueError: If the given FSA is not a DFA.
    """
    if FSAType.DFA not in dfa.type:
        raise ValueError(
            f"Expected an FSA of type {FSAType.DFA}. " f"Got an FSA of type {dfa.type}."
        )

    current_state: State = dfa.initial_state

    for symbol in word:
        next_states: set[State] = dfa.delta(current_state, symbol)

        # no next state so we hit a dead-end which means the word
        # is not accepted
        if not next_states:
            return False

        # since we are traversing a DFA the set only has one state
        current_state = next_states.pop()

    return current_state in dfa.final_states


def accepts(fsa: FSA, word: str) -> bool:
    """Return True if the FSA accepts the given word otherwise
    False."""
    return _dfa_accepts(subset_construction(fsa), word)
