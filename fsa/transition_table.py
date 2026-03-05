from __future__ import annotations
from .state import State
from typing import override, Mapping, Callable, AbstractSet
from lib import ObservableSet

class TransitionTable(dict[tuple[State, str], ObservableSet[State]]):
    """Represents the transition table for an FSA."""

    # a key in the transition table (state and symbol)
    type Key = tuple[State, str]
    # a value in the transition table (set of next states)
    type Value = ObservableSet[State]
    # a hook function for whenever the table is mutated
    type OnSetItemHook = Callable[[Key, AbstractSet[State]], None]
    # a hook function for when a value in a key-value pair is mutated
    type OnValueMutateHook = ObservableSet.Hook[State]

    # hook function to run before an item is set in the table
    _pre_setitem: OnSetItemHook | None
    # hook function to run before a state is added to a set of next states 
    _pre_value_add: OnValueMutateHook | None
    # hook function to run before a state is removed from a set of next states
    _pre_value_discard: OnValueMutateHook | None
    # hook function to run after a state is added to a set of next states
    _post_value_add: OnValueMutateHook | None
    # hook function to run after a state is removed from a set of next states
    _post_value_discard: OnValueMutateHook | None

    def __init__(
        self, 
        entries: Mapping[Key, AbstractSet[State]] | None = None,
        pre_setitem: OnSetItemHook | None = None,
        pre_value_add: OnValueMutateHook | None = None,
        pre_value_discard: OnValueMutateHook | None = None,
        post_value_add: OnValueMutateHook | None = None,
        post_value_discard: OnValueMutateHook | None = None,
    ):
        super().__init__()
    
        self._pre_setitem = pre_setitem
        self._pre_value_add = pre_value_add
        self._post_value_add = post_value_add
        self._pre_value_discard = pre_value_discard
        self._post_value_discard = post_value_discard

        if entries is not None:
            for key, value in entries.items():
                self[key] = value

    @override
    def __setitem__(self, key: Key, value: AbstractSet[State]) -> None:
        """Set an item in the transition table, running the pre-set-item hook."""
        if self._pre_setitem is not None:
            self._pre_setitem(key, value)

        super().__setitem__(
            key, 
            ObservableSet[State](
                value,
                pre_add=self._pre_value_add,
                post_add=self._post_value_add,
                pre_discard=self._pre_value_discard,
                post_discard=self._post_value_discard
            )
        )
    
    def __missing__(self, key: Key) -> Value:
        """Add the key to the table, mapping to an empty observable set."""
        self[key] = ObservableSet[State](
            pre_add=self._pre_value_add,
            post_add=self._post_value_add,
            pre_discard=self._pre_value_discard,
            post_discard=self._post_value_discard
        )

        return self[key]

    def remove_such_that(
        self, 
        match: Callable[[State, str, Value], bool]
    ) -> None:
        """Remove items from the transition table based on the given 
        matching function.
        
        Args:
            match: A matching function that accepts the start state, symbol 
            and next states of the current item being processed and should 
            return True if the item is to be discarded or False otherwise.
        """
        def _callback(
            start_state: State, 
            symbol: str, 
            end_states: TransitionTable.Value
        ) -> None:
            if match(start_state, symbol, end_states):
                del self[(start_state, symbol)]
        
        self.for_each(_callback)

    def for_each(
        self,
        callback: Callable[[State, str, Value], None]
    ) -> None:
        """Run a callback for each item in the transition table.

        Args:
            callback: A callback that accepts the start state, symbol and 
            next states of the current item being processed.
        """
        for (start_state, symbol), end_states in list(self.items()):
            callback(start_state, symbol, end_states)
        
    def flatten(self) -> set[tuple[State, str, State]]:
        """Flatten all transitions in the table into a set of 3-tuples 
        (start state, symbol, next state)."""
        flattened_transitions: set[tuple[State, str, State]] = set()

        def _add_flattened(
            start_state: State, 
            symbol: str,
            next_states: TransitionTable.Value
        ) -> None:
            for next_state in next_states:
                flattened_transitions.add((start_state, symbol, next_state))
        
        self.for_each(_add_flattened)

        return flattened_transitions
        