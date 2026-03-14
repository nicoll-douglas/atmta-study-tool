from typing import AbstractSet
from lib import DisjointSetUnion, SetMap
from .state import State


class _MarkingTable(SetMap[State, bool]):
    """Represents a triangular marking table for performing FSA
    minimization."""

    # the states of the FSA to use in the marking table
    _states: AbstractSet[State]

    # type for keys in the marking table
    type Key = tuple[State, State]
    # type for values in the marking table, True = marked, False = unmarked
    type Value = bool

    def __init__(self, states: AbstractSet[State]):
        """Initialise all items in the marking table to False (unmarked)."""
        self._states = states
        states_list: list[State] = list(states)

        super().__init__(
            ((states_list[i], states_list[j]), False)
            for i in range(len(states_list) - 1)
            for j in range(i + 1, len(states_list))
        )

    @property
    def size(self) -> int:
        """Get the size of the marking table."""
        return len(self._states) - 1

    def mark(self, state_pair: Key) -> None:
        """Mark a state pair in the marking table."""
        self[state_pair] = True

    def unmark(self, state_pair: Key) -> None:
        """Unmark a state pair in the marking table."""
        self[state_pair] = False

    def is_marked(self, state_pair: Key) -> Value:
        """Return True if the given pair is marked or False otherwise."""
        return self[state_pair]

    def mark_initial(self, final_states: AbstractSet[State]) -> None:
        """Mark all state pairs consisting of a non-final and a final state.

        This performs the initial step of the minimization algorithm.
        """
        for row_state, col_state in self.keys():
            # initial marking, if one final and other not then mark (True)
            if (row_state in final_states) ^ (col_state in final_states):
                self.mark((row_state, col_state))

    def should_mark(self, state_pair_delta: Key) -> Value:
        """Return True if an original state pair should be marked depending
        on the state pair received after performing a transition, or False
        otherwise.

        Args:
            state_pair_delta: The state pair received after performing
            a transition in the FSA from the original state pair.
        """
        row_state: State
        col_state: State
        row_state, col_state = state_pair_delta

        if row_state == col_state:
            return False

        # if delta marked then should mark original
        return self.is_marked((row_state, col_state))

    def get_disjoint_set_unions(self) -> DisjointSetUnion[State]:
        """Get the disjoint set unions of all the states in the
        minimized FSA from the marking table depending on their mark status.

        If pairs A and B are unmarked and they contain a common state, then
        they are merged into a set. If a pair in the table is marked then each
        state will belong in its own individual set.
        """
        unions: DisjointSetUnion[State] = DisjointSetUnion[State](self._states)

        for (state_a, state_b), mark in self.items():
            if not mark:
                unions.union(state_a, state_b)

        return unions
