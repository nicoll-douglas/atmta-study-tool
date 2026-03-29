from __future__ import annotations
from .state import State
from typing import override
from atmta_study_tool._common.data_structures import ObservableMapping, ObservableSet
from collections.abc import Callable, Set, Iterable, Mapping
from functools import reduce
from ..types import StateLike, Transition, TransitionLike
from ..utils import state_from, states_from, validate_epsilon, transition_from


class TransitionTable(
    ObservableMapping[tuple[State, Transition], ObservableSet[State]]
):
    """Represents the transition table for an automaton."""

    # hook function to run before a state is added to a set of next states
    _pre_value_add: Callable[[State], None] | None = None
    # hook function to run before a state is added to a set of next states
    _post_value_add: Callable[[State], None] | None = None
    # hook function to run before a state is removed from a set of next states
    _pre_value_discard: Callable[[State], None] | None = None
    # hook function to run before a state is removed from a set of next states
    _post_value_discard: Callable[[State], None] | None = None

    def __init__(
        self,
        mapping: (
            Mapping[tuple[StateLike, TransitionLike], Set[StateLike]] | None
        ) = None,
    ):
        super().__init__()

        if mapping is not None:
            for key, value in mapping.items():
                self[key] = value

    def _value(self, value: Iterable[StateLike]) -> ObservableSet[State]:
        """Create an observable set with value-add and value-discard hooks for the given set of states."""
        # here we use lambdas to create closures and take advantage of late binding instead of passing direct attributes
        return ObservableSet[State](
            states_from(value),
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

    def _key(self, key: tuple[StateLike, TransitionLike]) -> tuple[State, Transition]:
        """Create a key in the transition table from a key-like tuple."""
        return (state_from(key[0]), transition_from(key[1]))

    @override
    def __setitem__(
        self, key: tuple[StateLike, TransitionLike], value: Set[StateLike]
    ) -> None:
        super().__setitem__(self._key(key), self._value(value))

    def __getitem__(
        self, key: tuple[StateLike, TransitionLike]
    ) -> ObservableSet[State]:
        return super().__getitem__(self._key(key))

    @override
    def __delitem__(self, key: tuple[StateLike, TransitionLike]) -> None:
        return super().__delitem__(self._key(key))

    def __missing__(self, key: tuple[State, Transition]) -> ObservableSet[State]:
        """Add the given key to the table, mapping to an empty observable set."""
        self[key] = set()

        return self[key]

    def remove_such_that(
        self, match: Callable[[tuple[State, Transition], ObservableSet[State]], bool]
    ) -> None:
        """Remove items from the transition table based on the given matching function.

        Args:
            match: A matching function that accepts the key and value of the current item being processed and that should return True if the item is to be discarded or False otherwise.
        """
        for key, value in list(self.items()):
            if match(key, value):
                del self[key]

    def transition_count(self, entity: Transition | State | None = None) -> int:
        """Return the number of transitions in the transition table involving the given symbol, the given state, or in total if none given."""
        if entity is None:
            return reduce(lambda sum, v: len(v) + sum, self.values(), 0)

        if isinstance(entity, State):
            return (
                self.incoming_transition_count(entity)
                + self.loop_transition_count(entity)
                + self.outgoing_transition_count(entity)
            )

        validate_epsilon(entity)

        def _reducer(
            sum: int,
            table_item: tuple[tuple[State, Transition], ObservableSet[State]],
        ) -> int:
            (_, transition_symbol), value = table_item

            if transition_symbol == entity:
                sum += len(value)

            return sum

        return reduce(
            _reducer,
            self.items(),
            0,
        )

    def incoming_transition_count(self, state: StateLike) -> int:
        """Return the number of incoming transitions to the given state."""
        state = state_from(state)

        def _reducer(
            sum: int, item: tuple[tuple[State, Transition], ObservableSet[State]]
        ) -> int:
            (start_state, _), next_states = item

            if state in next_states and start_state != state:
                sum += 1

            return sum

        return reduce(_reducer, self.items(), 0)

    def outgoing_transition_count(self, state: StateLike) -> int:
        """Return the number of outgoing transitions from the given state."""
        state = state_from(state)

        def _reducer(
            sum: int, item: tuple[tuple[State, Transition], ObservableSet[State]]
        ) -> int:
            (start_state, _), next_states = item

            if start_state == state:
                sum += len(next_states)

                # exclude the loop transition
                if state in next_states:
                    sum -= 1

            return sum

        return reduce(_reducer, self.items(), 0)

    def loop_transition_count(self, state: StateLike) -> int:
        """Return the number of loop transitions at the given state."""
        state = state_from(state)

        def _reducer(
            sum: int, item: tuple[tuple[State, Transition], ObservableSet[State]]
        ) -> int:
            (start_state, _), next_states = item

            if start_state == state and state in next_states:
                sum += 1

            return sum

        return reduce(_reducer, self.items(), 0)

    def flatten(self) -> set[tuple[State, Transition, State]]:
        """Return a list of transitions in the transition table as a set of 3-tuples."""
        return {
            (start_state, transition, next_state)
            for (start_state, transition), next_states in self.items()
            for next_state in next_states
        }
