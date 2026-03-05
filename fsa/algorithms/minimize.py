from ..fsa import FSA
from .subset_construction import subset_construction
from ..marking_table import MarkingTable
from ..state import State
from ..utils import get_state_union_groupings
from lib import UnionFinder, SetMap

def minimize(fsa: FSA) -> FSA:
    dfa: FSA = subset_construction(fsa)
    marking_table: MarkingTable = MarkingTable(dfa.states)

    marking_table.mark_initial(dfa.final_states)

    mark_made: bool = True

    while mark_made:
        mark_made = False
        
        for (row_state, col_state), mark in marking_table.items():
            if mark: continue

            for symbol in dfa.alphabet:
                next_row_state: State
                next_col_state: State
                (next_row_state,) = dfa.delta(row_state, symbol)
                (next_col_state,) = dfa.delta(col_state, symbol)

                if marking_table.should_mark(
                    (next_row_state, next_col_state)
                ):
                    marking_table.mark((row_state, col_state))
                    mark_made = True
                    break
    
    state_unions: UnionFinder[State] = marking_table.get_unions()
    groupings: dict[State, set[State]] = get_state_union_groupings(state_unions)

    min_dfa_state_map: SetMap[State, State] = SetMap[State, State](
        (merged_states, State(merged_states))
        for merged_states in groupings.values()
    ) 
    
    min_dfa_initial: State = min_dfa_state_map[
        groupings[state_unions.find(dfa.initial_state)]
    ]

    min_dfa: FSA = FSA(
        initial_state=min_dfa_initial,
        states=set(min_dfa_state_map.values()),
        alphabet=dfa.alphabet
    )

    for state in groupings.values():
        representative: State = next(iter(state))

        for symbol in dfa.alphabet:
            (next_state,) = dfa.delta(representative)

            min_dfa.transition_table[
                (
                    min_dfa_state_map[groupings[state_unions.find(representative)]], 
                    symbol
                )
            ] = min_dfa_state_map[groupings[state_unions.find(next_state)]]
        
        if state & dfa.final_states:
            min_dfa.final_states.add(min_dfa_state_map[state])

    return min_dfa
