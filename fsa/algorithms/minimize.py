from ..models.fsa import FSA
from ..models.marking_table import _MarkingTable
from ..models.state import State
from .subset_construction import subset_construction
from lib import DisjointSetUnion, SetMap


def _get_state_union_groupings(dsj: DisjointSetUnion[State]) -> dict[State, set[State]]:
    """Return a mapping of the root state to the corresponding disjoint of
    states based on the given disjoint set union."""
    groupings: dict[State, set[State]] = {}

    for state in dsj:
        root: State = dsj.find(state)

        if root not in groupings:
            groupings[root] = set()

        groupings[root].add(state)

    return groupings


def minimize(fsa: FSA) -> FSA:
    """Perform the FSA minimization algorithm on the given FSA to create
    and return a new, minimized FSA."""
    # step 1: turn the FSA into a complete DFA
    dfa: FSA = subset_construction(fsa)
    marking_table: _MarkingTable = _MarkingTable(dfa.states)

    # step 2: mark non-final and final state pairs
    marking_table.mark_initial(dfa.final_states)

    # step 3: make multiple passes performing the main minimization algorithm
    # until no marks can be made
    mark_made: bool = True

    while mark_made:
        mark_made = False

        for (row_state, col_state), mark in marking_table.items():
            if mark:
                continue

            for symbol in dfa.alphabet:
                next_row_state: State = dfa.delta(row_state, symbol).pop()
                next_col_state: State = dfa.delta(col_state, symbol).pop()

                # step 3.1: determine whether the current unmarked pair
                # should be marked
                if marking_table.should_mark((next_row_state, next_col_state)):
                    marking_table.mark((row_state, col_state))
                    mark_made = True
                    break

    # step 4: get the disjoint set unions of the states in the rows and columns
    state_unions: DisjointSetUnion[State] = marking_table.get_disjoint_set_unions()
    # step 4.1: get the actual state groupings
    groupings: dict[State, set[State]] = _get_state_union_groupings(state_unions)

    min_dfa_state_map: SetMap[State, State] = SetMap[State, State](
        (merged_states, State(merged_states)) for merged_states in groupings.values()
    )

    # representative state of the grouping containing the initial state
    initial_representative: State = state_unions.find(dfa.initial_state)

    min_dfa: FSA = FSA(
        initial_state=min_dfa_state_map[groupings[initial_representative]],
        states=set(min_dfa_state_map.values()),
        alphabet=dfa.alphabet,
    )

    # step 5: get a representative state of the group (already the key of
    # grouping here)
    for representative, min_dfa_state in groupings.items():
        # step 5.1: see where the state goes on every symbol
        for symbol in dfa.alphabet:
            next_state: State = dfa.delta(representative, symbol).pop()
            representative_of_next: State = state_unions.find(next_state)

            # step 5.2: add the transition to the transition table for the
            # groupings
            min_dfa.transition_table[
                (min_dfa_state_map[groupings[representative]], symbol)
            ] = {min_dfa_state_map[groupings[representative_of_next]]}

        # step 6: if the grouping contains a final state then it is also a final state
        if min_dfa_state & dfa.final_states:
            min_dfa.final_states.add(min_dfa_state_map[min_dfa_state])

    return min_dfa
