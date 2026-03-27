from ..models import FSA, State
from copy import deepcopy
from collections.abc import Set
from atmta_study_tool.language import Symbol

# a memo object that maps states in an FSA to its epsilon-closure
type _EpsilonClosureMap = dict[State, set[State]]


def _get_new_nfa_delta(
    state: State, symbol: Symbol, e_nfa: FSA, e_closure_memo: _EpsilonClosureMap
) -> set[State]:
    """Compute and return the set of next states for a starting state and symbol (transition) in the new epsilon-free NFA.

    Uses the formula: δ'(q, a) = E(δ(E(q), a)), where 'q' is the state, E is the epsilon closure function, and 'a' is the transition symbol.

    Args:
        state: The starting state of the transition.
        symbol: The transition symbol.
        e_nfa: The old epsilon-NFA that epsilon-removal is being performed on.
        e_closure_memo: An _EpsilonClosureMap memo object mapping states in the epsilon-NFA to their epsilon closures.
    """
    if state in e_closure_memo:
        e_closure: set[State] = e_closure_memo[state]
    else:
        e_closure = e_nfa.epsilon_closure({state})
        e_closure_memo[state] = e_closure

    return e_nfa.epsilon_closure(e_nfa.delta(e_closure, symbol))


def _is_new_nfa_final_state(
    epsilon_closure: set[State], e_nfa_final_states: Set[State]
) -> bool:
    """Return True if a state is a final state in the new epsilon-free NFA, otherwise False.

    Uses the formula: E(q) ∩ F != Ø, where q is the state, E is the epsilon closure function, and F is the set of final states in the epsilon-NFA. I.e, if the epsilon closure contains a final state then it is a final state.

    Args:
        epsilon_closure: The epsilon-closure of the state.
        e_nfa_final_states: The set of final states in the epsilon-NFA.
    """
    return len(e_nfa_final_states & epsilon_closure) != 0


def epsilon_remove(e_nfa: FSA) -> FSA:
    """Create and return an FSA free of epsilon-transitions using the epsilon removal algorithm.

    Args:
        e_nfa: An FSA with epsilon transitions.
    """
    nfa: FSA = FSA(
        initial_state=e_nfa.initial_state,
        states=e_nfa.states,
        alphabet=deepcopy(e_nfa.alphabet),
    )

    e_closure_map: _EpsilonClosureMap = {}

    for state in e_nfa.states:
        for symbol in e_nfa.alphabet:
            next_states: set[State] = _get_new_nfa_delta(
                state, symbol, e_nfa, e_closure_map
            )

            if next_states:
                nfa.transition_table[(state, symbol)] = next_states

        if _is_new_nfa_final_state(e_closure_map[state], e_nfa.final_states):
            nfa.final_states.add(state)

    return nfa
