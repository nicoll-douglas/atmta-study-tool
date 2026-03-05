from typing import TYPE_CHECKING, AbstractSet
from lib import UnionFinder, SetMap

if TYPE_CHECKING:
    from .state import State

class MarkingTable(SetMap[State, bool]):
    _row: list[State]
    _col: list[State]
    _states: AbstractSet[State]

    type Key = tuple[State, State]
    type Value = bool
    
    def __init__(self, states: AbstractSet[State]):
        self._states = states

        states_list: list[State] = list(states)

        self._row = states_list[1:]
        self._col = states_list[0:-1]

        super(
            ((self._row[i], self._col[i]), False)
            for i in range(self.size)
        )

    @property
    def size(self) -> int:
        return len(self._row) # or column length (both the same)

    def mark(self, state_pair: Key) -> None:
        self[state_pair] = True
    
    def unmark(self, state_pair: Key) -> None:
        self[state_pair] = False
    
    def is_marked(self, state_pair: Key):
        return self[state_pair]

    def mark_initial(self, final_states: AbstractSet[State]) -> None:
        for i in range(self.size):
            row_state: State = self._row[i]
            col_state: State = self._col[i]

            # initial marking, if one final and other not then mark (True)
            if (row_state in final_states) ^ (col_state in final_states):
                self.mark((row_state, col_state))

    def should_mark(self, key: Key) -> Value:
        row_state: State
        col_state: State
        row_state, col_state = key

        if row_state == col_state:
            return False
        
        # if marked then should mark
        return self.is_marked((row_state, col_state))
    
    def get_unions(self) -> UnionFinder[State]:
        state_merger: UnionFinder[State] = UnionFinder[State](self._states)
        
        for (state_a, state_b), mark in self.items():
            if not mark:
                state_merger.union(state_a, state_b)

        return state_merger