from typing import TYPE_CHECKING
from .subset_construction import subset_construction

if TYPE_CHECKING:
    from ..fsa import FSA
    from ..state import State

def complement(fsa: FSA) -> FSA:
    """Create and return the complement automaton of the given FSA."""
    dfa: FSA = subset_construction(fsa, complete=True)
    non_final_states: set[State] = dfa.states - dfa.final_states

    dfa.final_states = non_final_states

    return dfa