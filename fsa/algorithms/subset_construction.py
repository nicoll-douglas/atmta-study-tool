from __future__ import annotations
from ..models.fsa import FSA
from ..models.state import State
from collections import deque
from copy import deepcopy
from typing import TYPE_CHECKING
from collections.abc import Set

if TYPE_CHECKING:
    from language.models import Symbol


class _NewDFAState:
    """Represents a state in the new DFA being computed via subset construction."""

    # the set of FSA states in the old FSA that comprise the new DFA state
    _states: frozenset[State]
    # the actual state object that will be given to the new DFA
    _state_obj: State

    def __init__(self, states: Set[State]):
        self._states = frozenset(states)
        # sorting here means each state object produced from the same set of states will be equivalent as they will have the same UID
        state_obj_uid: str = "{" + ", ".join(sorted(str(s) for s in states)) + "}"
        self._state_obj = State(state_obj_uid)

    @property
    def STATE_OBJ(self) -> State:
        return self._state_obj

    @property
    def STATES(self) -> frozenset[State]:
        return self._states

    def is_final(self, old_fsa: FSA) -> bool:
        """Return True if the DFA state is a final state, otherwise False.

        Uses the formula: S ∩ F != Ø.
        """
        return len(self.STATES & old_fsa.final_states) != 0

    def delta(self, symbol: Symbol, old_fsa: FSA) -> _NewDFAState:
        """Get the delta for the DFA state for the given symbol.

        Uses the formula: δ'(S, a) = ∪(s∈S) E(δ(s, a)).
        """
        next_state: set[State] = set()

        for old_fsa_state in self.STATES:
            next_state |= old_fsa.epsilon_closure(old_fsa.delta(old_fsa_state, symbol))

        return _NewDFAState(next_state)

    @staticmethod
    def get_new_dfa_initial_state(old_fsa: FSA) -> _NewDFAState:
        """Compute the initial state of the new DFA.

        Uses the formula: q_0' = E({q_0})
        """
        return _NewDFAState(old_fsa.epsilon_closure({old_fsa.initial_state}))


def subset_construction(fsa: FSA, complete: bool = True) -> FSA:
    """Construct an equivalent DFA from the given FSA via the subset construction algorithm.

    Args:
        complete: Whether the resulting DFA should be a complete DFA.

    Returns:
        An equivalent DFA.
    """
    # get the DFA's initial state (NFA epsilon closure)
    dfa_initial_state: _NewDFAState = _NewDFAState.get_new_dfa_initial_state(fsa)

    dfa: FSA = FSA(
        initial_state=dfa_initial_state.STATE_OBJ,
        states={dfa_initial_state.STATE_OBJ},
        final_states=(
            {dfa_initial_state.STATE_OBJ} if dfa_initial_state.is_final(fsa) else None
        ),
        alphabet=deepcopy(fsa.alphabet),
    )

    states_unprocessed: deque[_NewDFAState] = deque([dfa_initial_state])

    # discover all DFA states and construct the DFA transition table
    while states_unprocessed:
        current_dfa_state: _NewDFAState = states_unprocessed.popleft()

        for symbol in fsa.alphabet:
            # get the delta
            discovered_state: _NewDFAState = current_dfa_state.delta(symbol, fsa)

            if not complete and not discovered_state:
                continue

            # check if the state hasn't already been discovered
            if discovered_state.STATE_OBJ not in dfa.states:
                dfa.states.add(discovered_state.STATE_OBJ)

                # check whether this new discovered state is final and add it if so
                if discovered_state.is_final(fsa):
                    dfa.final_states.add(discovered_state.STATE_OBJ)

                # add the new discovered state for processing
                states_unprocessed.append(discovered_state)

            # add the transition to the transition table
            dfa.transition_table[(current_dfa_state.STATE_OBJ, symbol)] = {
                discovered_state.STATE_OBJ
            }

    return dfa
