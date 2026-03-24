from .fsa_type import FSAType
from .transition_table import TransitionTable
from collections import deque
from _common.data_structures import ObservableSet, ObservableSetController
from language import Alphabet, Word
from collections.abc import Set
from language import Symbol
from .state import State


class FSA:
    """Represents a Finite State Automaton (FSA)."""

    # the initial state of the FSA
    _initial_state: State
    # all possible states of the FSA
    _states: ObservableSet[State]
    # the final states of the FSA
    _final_states: ObservableSet[State]
    # the transition table of the FSA
    _transition_table: TransitionTable
    # the alphabet of the FSA
    _alphabet: Alphabet

    def __init__(
        self,
        initial_state: State,
        states: Set[State],
        alphabet: Alphabet | None = None,
        transition_table: TransitionTable | None = None,
        final_states: Set[State] | None = None,
    ):
        self.initial_state = initial_state
        self.states = states
        self.alphabet = alphabet if alphabet is not None else Alphabet()
        self.final_states = final_states if final_states is not None else set()
        self.transition_table = (
            transition_table if transition_table is not None else TransitionTable()
        )

    @property
    def states(self) -> ObservableSet[State]:
        return self._states

    @states.setter
    def states(self, new_value: Set[State]) -> None:
        if self.initial_state not in new_value:
            raise ValueError(
                f"Expected a set of states containing the initial state {self.initial_state!r}. Got {new_value}."
            )

        def _pre_discard(state: State) -> None:
            if state == self.initial_state:
                raise ValueError(
                    f"Expected a non-initial state. Got initial state {state!r}."
                )

        def _post_discard(state: State) -> None:
            self.final_states.discard(state)

            self.transition_table.remove_such_that(lambda key, _: key[0] == state)

            for next_states in self.transition_table.values():
                next_states.discard(state)

        self._states = ObservableSet[State](
            new_value, post_discard=_post_discard, pre_discard=_pre_discard
        )

        if hasattr(self, "_final_states"):
            self.final_states -= self.final_states - new_value

        if hasattr(self, "_transition_table"):
            self.transition_table.remove_such_that(
                lambda key, _: key[0] not in new_value
            )

            for next_states in self.transition_table.values():
                next_states -= next_states - new_value

    @property
    def initial_state(self) -> State:
        return self._initial_state

    @initial_state.setter
    def initial_state(self, new_value: State) -> None:
        if hasattr(self, "_states"):
            self._validate_states_contain(new_value)

        self._initial_state = new_value

    @property
    def final_states(self) -> ObservableSet[State]:
        return self._final_states

    @final_states.setter
    def final_states(self, new_value: Set[State]) -> None:
        self._final_states = ObservableSet[State](
            new_value, pre_add=self._validate_states_contain
        )

    @property
    def alphabet(self) -> Alphabet:
        return self._alphabet

    @alphabet.setter
    def alphabet(self, new_value: Alphabet) -> None:
        def _post_discard(symbol: Symbol) -> None:
            self.transition_table.remove_such_that(lambda key, _: symbol == key[1])

        ObservableSetController.set__post_discard(new_value, _post_discard)

        self._alphabet = new_value

        if hasattr(self, "_transition_table"):
            self.transition_table.remove_such_that(
                lambda key, _: key[1] not in new_value
            )

    @property
    def transition_table(self) -> TransitionTable:
        return self._transition_table

    @transition_table.setter
    def transition_table(self, new_value: TransitionTable) -> None:
        def _pre_setitem(
            key: TransitionTable.Key, value: TransitionTable.Value
        ) -> None:
            start_state: State
            symbol: Symbol | Word
            start_state, symbol = key

            self._validate_states_contain(start_state)

            if symbol not in self.alphabet and symbol != Word.EPSILON:
                raise ValueError(
                    f"Expected a symbol in the alphabet {self.alphabet} or {Word.EPSILON}. Got {symbol!r}."
                )

            if not value <= self.states:
                raise ValueError(
                    f"Expected the set of next states to be a subset of the set of states {self.states}. Got {value}."
                )

        new_value._pre_setitem = _pre_setitem

        # set all key-value pairs again to run our pre-setitem validation
        for key, value in new_value.items():
            new_value[key] = value

        new_value._pre_value_add = self._validate_states_contain

        self._transition_table = new_value

    def type(self) -> FSAType:
        """Gets bitwise flags indicating the type of the FSA."""
        # ideal scenario, complete and DFA
        type: FSAType = FSAType.DFA | FSAType.COMPLETE

        # check epsilon transitions
        if any(
            symbol == Word.EPSILON and next_states
            for (_, symbol), next_states in self.transition_table.items()
        ):
            # set NFA and EPSILON_NFA, remove DFA
            type = (type & ~FSAType.DFA) | FSAType.NFA | FSAType.EPSILON_NFA

        for state in self.states:
            for symbol in self.alphabet:
                next_state_count: int = len(self.delta(state, symbol))

                # more than 1 outgoing transition for the same letter
                if next_state_count > 1:
                    # remove DFA, add NFA
                    type = (type & ~FSAType.DFA) | FSAType.NFA

                # no transitions
                if next_state_count == 0:
                    # remove complete
                    type &= ~FSAType.COMPLETE

        return type

    def unreachable_states(self) -> set[State]:
        """Return the set of unreachable states in the FSA i.e states that cannot be reached from the initial state."""
        visited: set[State] = {self.initial_state}
        queue: deque[State] = deque([self.initial_state])

        while queue:
            current_state: State = queue.popleft()

            for (start_state, _), next_states in self.transition_table.items():
                if start_state == current_state:
                    unvisited: Set[State] = next_states - visited
                    visited |= unvisited
                    queue.extend(unvisited)

        return set(self.states - visited)

    def remove_unreachable_states(self) -> set[State]:
        """Remove all unreachable states from the FSA."""
        unreachable_states: set[State] = self.unreachable_states()

        self.states -= unreachable_states

        return unreachable_states

    def unproductive_states(self) -> set[State]:
        """Return the set of unproductive states in the FSA i.e non-initial states that cannot reach a final state."""
        productive_states: set[State] = set(self.final_states)
        state_added: bool = True

        while state_added:
            state_added = False

            for (start_state, _), next_states in self.transition_table.items():
                if productive_states & next_states:
                    if start_state not in productive_states:
                        productive_states.add(start_state)
                        state_added = True

        return set(self.states - productive_states - {self.initial_state})

    def remove_unproductive_states(self) -> set[State]:
        """Remove all unproductive states from the FSA."""
        unproductive_states: set[State] = self.unproductive_states()

        self.states -= unproductive_states

        return unproductive_states

    def delta(self, states: State | Set[State], symbol: Symbol | Word) -> set[State]:
        """Get the set of next states for a given state (or given states) and symbol in the transition table."""
        if isinstance(states, State):
            return set(self.transition_table[(states, symbol)])

        delta_states: set[State] = set()

        for state in states:
            delta_states |= self.transition_table[(state, symbol)]

        return delta_states

    def epsilon_closure(self, states: Set[State]) -> set[State]:
        """Get the epsilon-closure of a set of states in the FSA.

        Args:
            states: The set of starting states from which to start considering epsilon transitions.

        Returns:
            The epsilon-closure which contains all states that can be reached by only following epsilon-transitions from the given states. At minimum this will be a set states including all the given states.
        """
        closure: set[State] = set(states)
        queue: deque[State] = deque(closure)

        while queue:
            current_state: State = queue.popleft()
            next_states: set[State] = self.delta(current_state, Word.EPSILON)

            for state in next_states:
                if state not in closure:
                    closure.add(state)
                    queue.append(state)

        return closure

    def _validate_states_contain(self, state: State) -> None:
        """Validate that the given state is in the set of states of the FSA."""
        if state not in self.states:
            raise ValueError(
                f"Expected a state in the set of states {self.states}. Got {state!r}."
            )
