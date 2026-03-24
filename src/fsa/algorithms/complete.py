from ..models import State, FSA
from copy import deepcopy
from _common.utils import create_unique_objs_amongst


def complete(fsa: FSA) -> FSA:
    """Create and return a complete version of the FSA.

    That is, for every state-symbol pair that is missing, create a transition pointing to a dead state.
    """
    complete_fsa: FSA = deepcopy(fsa)
    dead_state: State = create_unique_objs_amongst(
        complete_fsa.states,
        initial=State("d"),
        factory=lambda counter: State(f"d_{counter}"),
    ).pop()
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
