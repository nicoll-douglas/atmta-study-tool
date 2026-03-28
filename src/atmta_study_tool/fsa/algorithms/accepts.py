from ..models import FSAType, State, FSA
from .subset_construction import subset_construction
from atmta_study_tool.language import Word


def accepts(fsa: FSA, word: Word) -> bool:
    """Return True if the FSA accepts the given word otherwise False."""
    dfa: FSA = subset_construction(fsa, complete=False)

    assert FSAType.DFA in dfa.type()

    current_state: State = dfa.initial_state

    for symbol in word:
        next_states: set[State] = dfa.delta(current_state, symbol)

        if not next_states:
            # no next state so we hit a dead-end which means the word is not accepted
            return False

        # since we are traversing a DFA the set only has one state
        current_state = next_states.pop()

    # the word is accepted if after finishing traversal, the current state is a final state
    return current_state in dfa.final_states
