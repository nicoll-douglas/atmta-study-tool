from atmta_study_tool._common.data_structures import (
    ObservableSet,
    ObservableSetController,
)
from .state import State
from .transition_table import TransitionTable
from atmta_study_tool.language import Alphabet, Symbol
from collections.abc import Set
from abc import ABC, abstractmethod
from collections import deque


class AbstractFSA[U: (str, frozenset[State]) = str](ABC):
    """Represents an abstract Finite-State Automaton (FSA).

    Args:
        U: The type of state UIDs in the FSA.
    """

    # the initial state of the FSA
    _initial_state: State[U]
    # all possible states of the FSA
    _states: ObservableSet[State[U]]
    # the final states of the FSA
    _final_states: ObservableSet[State[U]]
    # the transition table of the FSA
    _transition_table: TransitionTable[U]
    # the alphabet of the FSA
    _alphabet: Alphabet

    def __init__(
        self,
        initial_state: State[U],
        states: Set[State[U]],
        alphabet: Alphabet | None = None,
        transition_table: TransitionTable[U] | None = None,
        final_states: Set[State[U]] | None = None,
    ):
        self.initial_state = initial_state
        self.states = states
        self.alphabet = alphabet if alphabet is not None else Alphabet()
        self.final_states = final_states if final_states is not None else set()
        self.transition_table = (
            transition_table if transition_table is not None else TransitionTable()
        )

    @property
    def states(self) -> ObservableSet[State[U]]:
        return self._states

    @states.setter
    def states(self, new_value: Set[State[U]]) -> None:
        if self.initial_state not in new_value:
            raise ValueError(
                f"Expected a set of states containing the initial state {self.initial_state!r}. Got {new_value!r}."
            )

        def _pre_discard(state: State[U]) -> None:
            if state == self.initial_state:
                raise ValueError(
                    f"Expected a non-initial state. Got initial state {state!r}."
                )

        def _post_discard(state: State[U]) -> None:
            self.final_states.discard(state)

            self.transition_table.remove_such_that(lambda key, _: key[0] == state)

            for next_states in self.transition_table.values():
                next_states.discard(state)

        self._states = ObservableSet[State[U]](
            new_value, post_discard=_post_discard, pre_discard=_pre_discard
        )

        if hasattr(self, "_final_states"):
            self.final_states -= self.final_states - new_value

        if hasattr(self, "_transition_table"):
            self.transition_table.remove_such_that(
                lambda key, _: key[0] not in self.states
            )

            for next_states in self.transition_table.values():
                next_states -= next_states - self.states

    @property
    def initial_state(self) -> State[U]:
        return self._initial_state

    @initial_state.setter
    def initial_state(self, new_value: State[U]) -> None:
        if hasattr(self, "_states"):
            self._validate_states_contain(new_value)

        self._initial_state = new_value

    @property
    def final_states(self) -> ObservableSet[State[U]]:
        return self._final_states

    @final_states.setter
    def final_states(self, new_value: Set[State[U]]) -> None:
        self._final_states = ObservableSet[State[U]](
            new_value, pre_add=self._validate_states_contain
        )

    @property
    def alphabet(self) -> Alphabet:
        return self._alphabet

    @alphabet.setter
    def alphabet(self, new_value: Alphabet) -> None:
        def _post_discard(symbol: Symbol) -> None:
            self.transition_table.remove_such_that(lambda key, _: symbol == key[1])

        ObservableSetController(new_value).set_post_discard(_post_discard)

        old_alphabet: Alphabet = self.alphabet
        self._alphabet = new_value

        if hasattr(self, "_transition_table"):
            self.transition_table.remove_such_that(
                lambda key, _: key[1] in (old_alphabet - self.alphabet)
            )

    @property
    def transition_table(self) -> TransitionTable[U]:
        return self._transition_table

    @transition_table.setter
    def transition_table(
        self,
        new_value: TransitionTable[U],
    ) -> None:
        new_value._validate_symbol = self._validate_symbol
        new_value._validate_state = self._validate_states_contain

        # set all key-value pairs again to run our pre-setitem validation
        for key, value in new_value.items():
            new_value[key] = value

        self._transition_table = new_value

    def unreachable_states(self) -> set[State[U]]:
        """Return the set of unreachable states in the FSA i.e states that cannot be reached from the initial state."""
        visited: set[State[U]] = {self.initial_state}
        queue: deque[State[U]] = deque([self.initial_state])

        while queue:
            current_state: State[U] = queue.popleft()

            for (start_state, _), next_states in self.transition_table.items():
                if start_state == current_state:
                    unvisited: Set[State[U]] = next_states - visited
                    visited |= unvisited
                    queue.extend(unvisited)

        return set(self.states - visited)

    def remove_unreachable_states(self) -> set[State[U]]:
        """Remove all unreachable states from the FSA."""
        unreachable_states: set[State[U]] = self.unreachable_states()

        self.states -= unreachable_states

        return unreachable_states

    def unproductive_states(self) -> set[State[U]]:
        """Return the set of unproductive states in the FSA i.e non-initial states that cannot reach a final state."""
        productive_states: set[State[U]] = set(self.final_states)
        state_added: bool = True

        while state_added:
            state_added = False

            for (start_state, _), next_states in self.transition_table.items():
                if productive_states & next_states:
                    if start_state not in productive_states:
                        productive_states.add(start_state)
                        state_added = True

        return set(self.states - productive_states - {self.initial_state})

    def remove_unproductive_states(self) -> set[State[U]]:
        """Remove all unproductive states from the FSA."""
        unproductive_states: set[State[U]] = self.unproductive_states()

        self.states -= unproductive_states

        return unproductive_states

    def delta(self, states: State[U] | Set[State[U]], symbol: Symbol) -> set[State[U]]:
        """Get the set of next states for a given state (or given states) and given symbol in the transition table."""
        if not isinstance(states, Set):
            return set(self.transition_table[(states, symbol)])

        delta_states: set[State[U]] = set()

        for state in states:
            delta_states |= self.transition_table[(state, symbol)]

        return delta_states

    def _validate_states_contain(self, state: State) -> None:
        """Validate that the given state is in the set of states of the FSA."""
        if state not in self.states:
            raise ValueError(
                f"Expected a state in the set of states {self.states}. Got {state!r}."
            )

    @abstractmethod
    def _validate_symbol(self, symbol: Symbol) -> None:
        """Validate that the given symbol is a valid assignment for a transition in the transition table."""
        if symbol not in self.alphabet:
            raise ValueError(
                f"Expected a symbol in the alphabet {self.alphabet}. Got {symbol!r}."
            )
