from atmta_study_tool._common.data_structures import SetDict
from .state import State
from collections.abc import Set, Collection


class MarkingTable(SetDict[State, bool]):
    """Represents a triangular marking table for performing FSA minimization.

    The following illustrates a representation of a table for an FSA with states 0, 1, 2, and 3, where the row states 1, 2, 3 and col states are 0, 1, 2:

    1|_|_
    2|_|_|_
    3|_|_|_|
      0 1 2

    Since we extend SetDict, the order of row-col state pairs that define the keys don't actually matter which is expected of a triangular marking table.
    """

    _states: frozenset[State]
    _row_states: tuple[State, ...]
    _col_states: tuple[State, ...]
    _row_states_set: set[State]
    _col_states_set: set[State]

    # type for keys used for access with the marking table
    type Key = Collection[State]
    # type for values in the marking table, True = marked, False = unmarked
    type Value = bool

    def __init__(self, states: Set[State]):
        """Initialise all items in the marking table to False (unmarked)."""
        self._states = frozenset(states)
        states_list: tuple[State, ...] = tuple(states)
        self._row_states = states_list[1:]
        self._col_states = states_list[:-1]
        self._row_states_set = set(self._row_states)
        self._col_states_set = set(self._col_states)

        super().__init__(
            {
                (self._row_states[j], self._col_states[i]): False
                for i in range(self.SIZE)
                for j in range(i, self.SIZE)
            }
        )

    def __setitem__(self, key: Key, value: bool):
        if len(key) != 2:
            raise ValueError(f"Expected a key of length 2. Got {key!r}.")

        first_state: State
        second_state: State
        first_state, second_state = key

        if not (
            first_state in self._row_states_set and second_state in self._col_states_set
        ) and not (
            first_state in self._col_states_set and second_state in self._row_states_set
        ):
            raise ValueError(
                f"Expected a key with a state in the set of states {self._row_states_set!r} and a state in the set of states {self._col_states_set!r}. Got {key!r}."
            )

        return super().__setitem__(key, value)

    # prevent removal of squares in the marking table
    def __delitem__(self, key: Key) -> None:
        raise TypeError(
            f"'{self.__class__.__name__}' object does not support item deletion."
        )

    @property
    def SIZE(self) -> int:
        """Get the size of the marking table."""
        return len(self._row_states)  # or self._col_states

    @property
    def COL_STATES(self) -> tuple[State, ...]:
        return self._col_states

    @property
    def ROW_STATES(self) -> tuple[State, ...]:
        return self._row_states

    @property
    def STATES(self) -> frozenset[State]:
        return self._states

    def mark(self, state_pair: Key) -> None:
        """Mark a state pair in the marking table."""
        self[state_pair] = True

    def unmark(self, state_pair: Key) -> None:
        """Unmark a state pair in the marking table."""
        self[state_pair] = False

    def marked(self, state_pair: Key) -> Value:
        """Return True if the given pair is marked or False otherwise."""
        return self[state_pair]
