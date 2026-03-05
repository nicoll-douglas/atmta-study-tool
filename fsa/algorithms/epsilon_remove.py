from ..fsa import FSA
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..state import State

def epsilon_remove(fsa: FSA) -> FSA:
    """Create and return an FSA free of epsilon-transitions using the 
    epsilon removal algorithm.

    The formula used to calculate the new transition table is the 
    following: δ'(q, a) = E(δ(E(q), a)) where E is the epsilon closure 
    function.    
    """
    nfa: FSA = FSA(
        initial_state=fsa.initial_state,
        states={fsa.initial_state},
        alphabet=fsa.alphabet
    )

    e_closures: dict[State, frozenset[State]] = {
        state: fsa.epsilon_closure(state)
        for state in fsa.states
    }

    # step 1: iterate over the states
    for state in fsa.states:
        nfa.states.add(state)

        # step 2: iterate over the alphabet
        for symbol in fsa.alphabet:
            # step 2.1: use the formula for δ': δ'(q, a) = E(δ(E(q), a))
            next_states: frozenset[State] = fsa.epsilon_closure(
                fsa.delta(e_closures[state], symbol)
            )

            if next_states:
                nfa.states |= next_states
                nfa.transition_table[(state, symbol)] = next_states

        # step 3: identify the final states such that: E(q) ∩ F != Ø
        if fsa.final_states & e_closures[state]: 
            nfa.final_states.add(state)
    
    return nfa