from __future__ import annotations
from collections import deque, defaultdict
from typing import AbstractSet
from .state import State
from ..constants import EPSILON
from .transition_table import _TransitionTable
from .. import _hooks
from lib import ObservableSet
from .fsa_type import FSAType


class FSA:
    """Represents a Finite State Automaton (FSA) and contains algorithms
    that operate on it."""

    # the initial state of the FSA
    _initial_state: State
    # all possible states of the FSA
    _states: ObservableSet[State]
    # the final states of the FSA
    _final_states: ObservableSet[State]
    # the transition table of the FSA
    _transition_table: _TransitionTable
    # the alphabet of the FSA
    _alphabet: ObservableSet[str]

    def __init__(
        self,
        initial_state: State,
        states: AbstractSet[State],
        alphabet: AbstractSet[str] | None = None,
        transitions: AbstractSet[tuple[State, str, State]] | None = None,
        final_states: AbstractSet[State] | None = None,
    ):
        self._initial_state = initial_state
        self._states = self._states_from_set(set())
        self.states = states
        self._alphabet = self._alphabet_from_set(alphabet)
        self.final_states = final_states
        self.transition_table = transitions

    @property
    def states(self) -> ObservableSet[State]:
        return self._states

    @states.setter
    def states(self, value: AbstractSet[State]) -> None:
        """Set the states of the FSA.

        The new value is validated to make sure it contains the current
        initial state. As a side effect, any final states not in the new
        set of states are removed and any transitions involving states
        not in the new set of states are also removed.
        """
        _hooks.states.pre_set(
            new_states=value, current_initial_state=self.initial_state
        )

        states_to_add: set[State] = set(value) - self.states
        states_to_remove: set[State] = self.states - value

        for state in states_to_remove:
            self.states.discard(state)

        for state in states_to_add:
            self.states.add(state)

    @property
    def initial_state(self) -> State:
        return self._initial_state

    @initial_state.setter
    def initial_state(self, value: State) -> None:
        """Set the initial state of the FSA.

        The new state is validated to make sure it is a state in
        the current set of states.
        """
        _hooks.initial_state.pre_set(
            new_initial_state=value, current_states=self.states
        )

        self._initial_state = value

    @property
    def final_states(self) -> ObservableSet[State]:
        return self._final_states

    @final_states.setter
    def final_states(self, value: AbstractSet[State] | None) -> None:
        """Set the final states of the FSA.

        The new value is validated to make sure it only contains states
        in the current set of states.
        """
        self._final_states = self._final_states_from_set(value)

    @property
    def alphabet(self) -> ObservableSet[str]:
        return self._alphabet

    @alphabet.setter
    def alphabet(self, value: AbstractSet[str]) -> None:
        """Set the alphabet of the FSA.

        As a side effect, any transition involving a symbol not in the
        new alphabet is removed from the transition table.
        """
        self._alphabet = self._alphabet_from_set(value)

        _hooks.alphabet.post_set(
            new_alphabet=value, current_transition_table=self.transition_table
        )

    @property
    def transition_table(self) -> _TransitionTable:
        return self._transition_table

    @transition_table.setter
    def transition_table(
        self, value: AbstractSet[tuple[State, str, State]] | None
    ) -> None:
        """Set the transition table of the FSA.

        The new value is validated to make sure it's transitions only
        contain states in the current set of states and symbols in the
        current alphabet.
        """
        self._transition_table = self._transition_table_from_set(value)

    @property
    def type(self) -> FSAType:
        """Gets bitwise flags indicating the type of the FSA.

        If FSAType.EPSILON_NFA is set then FSAType.NFA is also
        set. FSAType.NFA and FSAType.DFA are mutually exclusive.
        """
        # ideal scenario, complete and DFA
        type: FSAType = FSAType.DFA | FSAType.COMPLETE

        if any(
            symbol == EPSILON and next_states
            for (_, symbol), next_states in self.transition_table.items()
        ):
            type = (type & ~FSAType.DFA) | FSAType.NFA | FSAType.EPSILON_NFA

        for state in self.states:
            for symbol in self.alphabet:
                next_state_count: int = len(self.delta(state, symbol))

                if next_state_count > 1:
                    type = (type & ~FSAType.DFA) | FSAType.NFA

                if next_state_count == 0:
                    type &= ~FSAType.COMPLETE

        return type

    def delta(self, state: State | AbstractSet[State], symbol: str) -> set[State]:
        """Get the set of next states for a state and symbol in the
        transition table.

        If a set of states is passed then the union of next states is
        returned for those states.
        """
        normalised_states: AbstractSet[State] = (
            {state} if isinstance(state, State) else state
        )

        return {
            next_state
            for start_state in normalised_states
            for next_state in self.transition_table[(start_state, symbol)]
        }

    def copy(self) -> FSA:
        """Create a copy of the FSA."""
        return FSA(
            initial_state=self.initial_state,
            states=self.states,
            final_states=self.final_states,
            transitions=self.transition_table.flatten(),
            alphabet=self.alphabet,
        )

    def epsilon_closure(self, states: AbstractSet[State] | State) -> set[State]:
        """Get the epsilon-closure of a state(s) in the FSA.

        Args:
            states: The state or set of starting states from which to start
            considering epsilon transitions.

        Returns:
            The epsilon-closure which contains all states
            that can be reached by only following epsilon-transitions
            from the given states. At minimum this will be a set states
            including all the given states.
        """
        normalised_states: set[State] = (
            {states} if isinstance(states, State) else set(states)
        )
        closure: set[State] = normalised_states
        queue: deque[State] = deque(normalised_states)

        while queue:
            current_state: State = queue.popleft()
            next_states: set[State] = self.delta(current_state, EPSILON)

            for state in next_states:
                if state not in closure:
                    closure.add(state)
                    queue.append(state)

        return closure

    def _states_from_set(
        self,
        states: AbstractSet[State],
    ) -> ObservableSet[State]:
        """Create and return a set of states for the class from the given
        set of states."""
        return ObservableSet[State](
            states,
            pre_add=lambda state: _hooks.states.pre_add(
                new_state=state, current_states=self.states
            ),
            post_discard=lambda state: _hooks.states.post_discard(
                state=state,
                current_final_states=self.final_states,
                current_transition_table=self.transition_table,
            ),
            pre_discard=lambda state: _hooks.states.pre_discard(
                state=state,
                current_initial_state=self.initial_state,
            ),
        )

    def _final_states_from_set(
        self, final_states: AbstractSet[State] | None = None
    ) -> ObservableSet[State]:
        """Create a set of final states for the class from the given set
        of final states."""
        return ObservableSet[State](
            final_states,
            pre_add=lambda state: _hooks.final_states.pre_add(
                new_final_state=state, current_states=self.states
            ),
        )

    def _alphabet_from_set(
        self, alphabet: AbstractSet[str] | None = None
    ) -> ObservableSet[str]:
        """Create an alphabet for the class from the given set of symbols."""
        return ObservableSet[str](
            alphabet,
            pre_add=lambda symbol: _hooks.alphabet.pre_add(symbol),
            post_discard=lambda symbol: _hooks.alphabet.post_discard(
                symbol=symbol, current_transition_table=self.transition_table
            ),
        )

    def _transition_table_from_set(
        self, transitions: AbstractSet[tuple[State, str, State]] | None = None
    ) -> _TransitionTable:
        """Create a transition table for the class from the given set of
        transitions.

        Args:
            transitions: A set of 3-tuples representing a transition with
            a start state, symbol and next state.
        """
        transition_data: defaultdict[tuple[State, str], set[State]] | None

        if transitions is not None:
            transition_data = defaultdict(set)

            for start_state, symbol, next_state in transitions:
                transition_data[(start_state, symbol)].add(next_state)
        else:
            transition_data = None

        return _TransitionTable(
            transition_data,
            pre_setitem=(
                lambda key, value: _hooks.transition_table.pre_setitem(
                    key=key,
                    value=value,
                    current_states=self.states,
                    current_alphabet=self.alphabet,
                )
            ),
            pre_value_add=lambda state: _hooks.transition_table.pre_value_add(
                new_state=state, current_states=self.states
            ),
        )
