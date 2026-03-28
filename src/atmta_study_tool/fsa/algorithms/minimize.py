from ..models import MarkingTable, FSA, State, FSAType
from .subset_construction import subset_construction
from atmta_study_tool._common.data_structures import DisjointSetUnion
from collections.abc import Set
from copy import deepcopy
from atmta_study_tool.language import Symbol


class _MinFSAState:
    """Represents a state in the new minimal FSA being computed via minimization."""

    # the set of FSA states in the old FSA that comprise the new min FSA state
    _states: frozenset[State]
    # the actual state object that will be given to the new FSA
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

    @staticmethod
    def get_min_fsa_states(
        marking_table_dsu: DisjointSetUnion[State],
    ) -> dict[State, _MinFSAState]:
        """Get the set of states in the minimal FSA as a dictionary mapping the representative of the state to the state.

        Args:
            marking_table_dsu: The disjoint set union of the marking table computed after marking.
        """
        return {
            representative: _MinFSAState(states)
            for representative, states in marking_table_dsu.sets().items()
        }


def _should_mark(
    state_pair: MarkingTable.Key,
    transition_symbol: Symbol,
    dfa: FSA,
    marking_table: MarkingTable,
) -> bool:
    """Return True if the given state pair should be marked in the given marking table, otherwise False.

    Args:
        state_pair: The state pair.
        transition_symbol: A transition symbol in the given FSA's alphabet.
        dfa: The FSA.
        marking_table: The marking table.
    """
    assert (FSAType.DFA | FSAType.COMPLETE) in dfa.type()

    row_state: State
    col_state: State
    row_state, col_state = state_pair
    next_row_state: State = dfa.delta(row_state, transition_symbol).pop()
    next_col_state: State = dfa.delta(col_state, transition_symbol).pop()

    if next_row_state == next_col_state:
        return False

    return marking_table.marked((next_row_state, next_col_state))


def _mark_initial(marking_table: MarkingTable, fsa: FSA) -> None:
    """Mark all state pairs consisting of a non-final and a final state in the given marking table for the given FSA."""
    for row_state, col_state in marking_table.keys():
        # mark if one state is final and the other non-final
        if (row_state in fsa.final_states) ^ (col_state in fsa.final_states):
            marking_table.mark((row_state, col_state))


def _perform_mark_passes(marking_table: MarkingTable, fsa: FSA) -> None:
    """Perform the main minimization routine of filling in the given marking table for the given FSA after initial marks have been made."""
    mark_made: bool = True

    while mark_made:
        mark_made = False

        for key, mark in marking_table.items():
            if mark:
                continue

            for symbol in fsa.alphabet:
                if _should_mark(key, symbol, fsa, marking_table):
                    marking_table.mark(key)
                    mark_made = True
                    break


def _get_marking_table_dsu(marking_table: MarkingTable) -> DisjointSetUnion[State]:
    """Get the disjoint set unions of all the states in the marking table depending on their mark status.

    If pairs A and B are unmarked and they contain a common state, then they are merged into a set, otherwise kept as individual 2-sets. If a pair in the table is marked then each state in the pair will belong in its own individual set.
    """
    unions: DisjointSetUnion[State] = DisjointSetUnion[State](marking_table.STATES)

    for (state_a, state_b), mark in marking_table.items():
        if not mark:
            unions.union(state_a, state_b)

    return unions


def minimize(fsa: FSA) -> FSA:
    """Perform the FSA minimization algorithm on the given FSA to create and return a new, minimized FSA."""

    dfa: FSA = subset_construction(fsa, complete=True)

    marking_table: MarkingTable = MarkingTable(dfa.states)

    _mark_initial(marking_table, dfa)
    _perform_mark_passes(marking_table, dfa)

    marking_table_dsu: DisjointSetUnion[State] = _get_marking_table_dsu(marking_table)
    min_fsa_states: dict[State, _MinFSAState] = _MinFSAState.get_min_fsa_states(
        marking_table_dsu
    )
    min_fsa_initial_state: _MinFSAState = min_fsa_states[
        marking_table_dsu.find(dfa.initial_state)
    ]

    min_dfa: FSA = FSA(
        initial_state=min_fsa_initial_state.STATE_OBJ,
        states={state.STATE_OBJ for state in min_fsa_states.values()},
        alphabet=deepcopy(dfa.alphabet),
    )

    for representative, min_fsa_state in min_fsa_states.items():
        for symbol in dfa.alphabet:
            next_dfa_state: State = dfa.delta(representative, symbol).pop()
            next_dfa_state_repr: State = marking_table_dsu.find(next_dfa_state)

            min_dfa.transition_table[(min_fsa_state.STATE_OBJ, symbol)] = {
                min_fsa_states[next_dfa_state_repr].STATE_OBJ
            }

        if min_fsa_state.STATES & dfa.final_states:
            min_dfa.final_states.add(min_fsa_state.STATE_OBJ)

    min_dfa.remove_unreachable_states()
    min_dfa.remove_unproductive_states()

    return min_dfa
