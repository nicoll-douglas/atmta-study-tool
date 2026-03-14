from ..models.state import State
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models.fsa import FSA


def complete(fsa: FSA) -> FSA:
    """Create and return a complete version of the FSA.

    That is, for every state-symbol pair that is missing, create a
    transition pointing to a dead state.
    """
    complete_fsa: FSA = fsa.copy()
    dead_state: State = State("d")
    found_missing: bool = False

    for state in set(complete_fsa.states):
        for symbol in complete_fsa.alphabet:
            if not fsa.delta(state, symbol):
                if not found_missing:
                    complete_fsa.states.add(dead_state)
                    found_missing = True

                fsa.transition_table[(state, symbol)] = {dead_state}

    if found_missing:
        for symbol in complete_fsa.alphabet:
            fsa.transition_table[(dead_state, symbol)] = {dead_state}

    return complete_fsa
