from ..models import State, FSA
from copy import deepcopy
from collections.abc import Set


def _create_new_dead_state(fsa_states: Set[State]) -> State:
    """Create a new dead state not in the given set of FSA states."""
    counter: int = 0
    dead_state: State = State(f"state_{counter}")

    while dead_state in fsa_states:
        counter += 1
        dead_state = State(f"state_{counter}")

    return dead_state


def complete(fsa: FSA) -> FSA:
    """Create and return a complete version of the FSA.

    That is, for every state-symbol pair that is missing, create a transition pointing to a dead state.
    """
    complete_fsa: FSA = deepcopy(fsa)
    dead_state: State = _create_new_dead_state(complete_fsa.states)
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
