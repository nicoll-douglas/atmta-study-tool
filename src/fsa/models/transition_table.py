from __future__ import annotations
from .state import State
from typing import override
from _common.data_structures import ObservableMapping, ObservableSet
from .state import State
from collections.abc import Callable, Set, Mapping
from language.models.symbol import Symbol
from language.models.word import Word

class TransitionTable(
    ObservableMapping[tuple[State, Symbol | Word], ObservableSet[State]]
):
    """Represents the transition table for an FSA."""

    type Key = tuple[State, Symbol | Word]
    type Value = ObservableSet[State]

    # hook function to run before a state is added to a set of next states
    _pre_value_add: Callable[[State], None] | None = None
    # hook function to run before a state is added to a set of next states
    _post_value_add: Callable[[State], None] | None = None
    # hook function to run before a state is removed from a set of next states
    _pre_value_discard: Callable[[State], None] | None = None
    # hook function to run before a state is removed from a set of next states
    _post_value_discard: Callable[[State], None] | None = None

    def __init__(self, mapping: Mapping[Key, Set[State]] | None = None):
        initial_table: dict[TransitionTable.Key, TransitionTable.Value] | None = (
            None
            if mapping is None
            else {k: self._create_observable_value(v) for k, v in mapping.items()}
        )

        super().__init__(initial_table)

    def _create_observable_value(self, value: Set[State] | None = None) -> Value:
        """Create an observable set with value-add and value-discard hooks for the given set of states."""
        # here we use lambdas to create closures and take advantage of late binding instead of passing direct attributes
        return ObservableSet[State](
            value,
            pre_add=lambda state: (
                None if self._pre_value_add is None else self._pre_value_add(state)
            ),
            post_add=lambda state: (
                None if self._post_value_add is None else self._post_value_add(state)
            ),
            pre_discard=lambda state: (
                None
                if self._pre_value_discard is None
                else self._pre_value_discard(state)
            ),
            post_discard=lambda state: (
                None
                if self._post_value_discard is None
                else self._post_value_discard(state)
            ),
        )

    @override
    def __setitem__(self, key: Key, value: Set[State]) -> None:
        super().__setitem__(
            key,
            (
                value
                if isinstance(value, ObservableSet)
                else self._create_observable_value(value)
            ),
        )

    def __missing__(self, key: Key) -> Value:
        """Add the given key to the table, mapping to an empty observable set."""
        new_value: TransitionTable.Value = self._create_observable_value()
        self[key] = new_value

        return new_value

    def remove_such_that(self, match: Callable[[Key, Value], bool]) -> None:
        """Remove items from the transition table based on the given matching function.

        Args:
            match: A matching function that accepts the key and value of the current item being processed and that should return True if the item is to be discarded or False otherwise.
        """
        for key, value in list(self.items()):
            if match(key, value):
                del self[key]
