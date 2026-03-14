from lib import SetMap
from ..models.state import State
from ..models.fsa import FSA
from collections import deque


def subset_construction(fsa: FSA, complete: bool = True) -> FSA:
    """Construct an equivalent deterministic FSA from the current
    FSA via the subset construction algorithm.

    Args:
        complete: Whether the resulting DFA should be a complete DFA.

    Returns:
        An equivalent DFA.
    """
    # step 1: get the DFA's initial state (NFA epsilon closure)
    dfa_initial_state: set[State] = fsa.epsilon_closure(fsa.initial_state)

    seen_states: SetMap[State, State] = SetMap[State, State](
        [(dfa_initial_state, State(dfa_initial_state))]
    )

    dfa: FSA = FSA(
        initial_state=seen_states[dfa_initial_state],
        states={seen_states[dfa_initial_state]},
        alphabet=set(fsa.alphabet),
    )

    # step 2: discover all DFA states and construct the DFA
    # transition table
    discovered_states: deque[set[State]] = deque([dfa_initial_state])

    while discovered_states:
        current_dfa_state: set[State] = discovered_states.popleft()

        # step 2.1: iterate over the alphabet
        for symbol in fsa.alphabet:
            # step 2.2: find the next DFA state using the formula:
            # δ'(Q, a) = E((∪ q∈Q) δ(q, a))
            next_dfa_state: set[State] = fsa.epsilon_closure(
                fsa.delta(current_dfa_state, symbol)
            )

            if not complete and not next_dfa_state:
                continue

            if next_dfa_state not in seen_states:
                seen_states[next_dfa_state] = State(next_dfa_state)
                dfa.states.add(seen_states[next_dfa_state])

                # step 2.3: add the state to the queue if undiscovered
                discovered_states.append(next_dfa_state)

            dfa.transition_table[(seen_states[current_dfa_state], symbol)] = {
                seen_states[next_dfa_state]
            }

    # step 3: identify the final states from the formula:
    # F' = {q | q ∈ Q' && q ∩ F != Ø}
    dfa.final_states = {
        dfa_state
        for nfa_states, dfa_state in seen_states.items()
        if nfa_states & fsa.final_states
    }

    return dfa
