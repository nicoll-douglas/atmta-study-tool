from __future__ import annotations
from collections import deque, defaultdict
from typing import AbstractSet
from .state import State
from .word import EPSILON
from .transition_table import TransitionTable
from . import hooks
from utils import ObservableSet
from .fsa_type import FSAType

"""
Algorithms to implement:
    - [x] Subset construction
    - [x] Epsilon removal
    - [ ] Complementation
    - [ ] Intersection (product automaton)
    - [ ] Minimisation
    
"""

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
    _transition_table: TransitionTable
    # the alphabet of the FSA
    _alphabet: ObservableSet[str]

    def __init__(
        self,
        initial_state: State,
        states: set[State],
        alphabet: AbstractSet[str] | None = None,
        transitions: AbstractSet[tuple[State, str, State]] | None = None,
        final_states: AbstractSet[State] | None = None
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
    def states(self, value: set[State]) -> None:
        """Set the states of the FSA.
        
        The new value is validated to make sure it contains the current 
        initial state. As a side effect, any final states not in the new 
        set of states are removed and any transitions involving states 
        not in the new set of states are also removed.
        """
        hooks.states.pre_set(
            new_states=value,
            current_initial_state=self.initial_state
        )

        states_to_add: set[State] = value - self.states
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
        hooks.initial_state.pre_set(
            new_initial_state=value,
            current_states=self.states
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

        hooks.alphabet.post_set(
            new_alphabet=value,
            current_transition_table=self.transition_table
        )
 
    @property
    def transition_table(self) -> TransitionTable:
        return self._transition_table
    
    @transition_table.setter
    def transition_table(
        self, 
        value: AbstractSet[tuple[State, str, State]] | None
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
        
        If FSAType.COMPLETE_DFA is set in the result then FSAType.DFA 
        is also set. If FSAType.EPSILON_NFA is set then FSAType.NFA is also 
        set. FSAType.NFA and FSAType.DFA are mutually exclusive.
        """
        if any(
            symbol == EPSILON
            and next_states
            for (_, symbol), next_states in self.transition_table.items()
        ): return FSAType.NFA | FSAType.EPSILON_NFA

        type: FSAType = FSAType.DFA | FSAType.COMPLETE_DFA

        for state in self.states:
            for symbol in self.alphabet:
                next_state_count: int = len(self.delta(state, symbol))

                if next_state_count > 1:
                    return FSAType.NFA
                
                if next_state_count == 0:
                    type = FSAType.DFA
        
        return type
 
    def delta(
        self, 
        state: State | AbstractSet[State], 
        symbol: str
    ) -> frozenset[State]:    
        """Get the set of next states for a state and symbol in the 
        transition table.

        If a set of states is passed then the union of next states is 
        returned for those states.
        """
        normalised_states: AbstractSet[State] = (
            {state} if isinstance(state, State) else state
        )

        return frozenset({
            next_state
            for start_state in normalised_states
            for next_state in self.transition_table[(start_state, symbol)]
        })

    def accepts(self, word: str) -> bool:
        """Return True if the FSA accepts the given word otherwise 
        False."""
        return FSA._dfa_accepts(self.subset_construction(), word)

    def recognizes_empty_language(self) -> bool:
        """Return True if the FSA recognzies the empty language (a set 
        with no words), otherwise False.
        """ 
        visited: set[State] = {self.initial_state}
        queue: deque[State] = deque([self.initial_state])

        while queue:
            current_state: State = queue.popleft()
            
            if current_state in self.final_states:
                return False
            
            for (start_state, _), next_states in (
                self.transition_table.items()
            ):
                if start_state == current_state:
                    for next_state in next_states:
                        if next_state not in visited:
                            visited.add(next_state)
                            queue.append(next_state)
                            
        return True

    def recognizes(self, language: set[str]) -> bool:
        """Return True if the FSA recognizes the given language, 
        otherwise False."""
        if not language: return self.recognizes_empty_language()

        dfa: FSA = self.subset_construction()

        return all(FSA._dfa_accepts(dfa, word) for word in language)
    
    def epsilon_removal(self) -> FSA:
        """Create and return an FSA free of epsilon-transitions using the 
        epsilon removal algorithm.

        The formula used to calculate the new transition table is the 
        following: δ'(q, a) = E(δ(E(q), a)) where E is the epsilon closure 
        function.    
        """
        nfa: FSA = FSA(
            initial_state=self.initial_state,
            states={self.initial_state},
            alphabet=self.alphabet
        )

        e_closures: dict[State, frozenset[State]] = {
            state: self.epsilon_closure(state)
            for state in self.states
        }

        # step 1: iterate over the states
        for state in self.states:
            nfa.states.add(state)

            # step 2: iterate over the alphabet
            for symbol in self.alphabet:
                # step 2.1: use the formula for δ': δ'(q, a) = E(δ(E(q), a))
                next_states: frozenset[State] = self.epsilon_closure(
                    self.delta(e_closures[state], symbol)
                )

                if next_states:
                    nfa.states |= next_states
                    nfa.transition_table[(state, symbol)] = next_states

            # step 3: identify the final states such that: E(q) ∩ F != Ø
            if self.final_states & e_closures[state]: 
                nfa.final_states.add(state)
        
        return nfa
        
    def epsilon_closure(
        self, 
        states: AbstractSet[State] | State
    ) -> frozenset[State]:
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
            {states}
            if isinstance(states, State)
            else set(states)
        )
        closure: set[State] = normalised_states
        queue: deque[State] = deque(normalised_states)

        while queue:
            current_state: State = queue.popleft()
            next_states: frozenset[State] = self.delta(current_state, EPSILON)

            for state in next_states:
                if state not in closure:
                    closure.add(state)
                    queue.append(state)

        return frozenset(closure)
    
    def subset_construction(self, complete: bool = True) -> FSA:
        """Construct an equivalent deterministic FSA from the current 
        FSA via the subset construction algorithm.

        Args:
            complete: Whether the resulting DFA should be a complete DFA.

        Returns:
            An equivalent DFA
        """
        # step 1: get the DFA's initial state (NFA epsilon closure)
        dfa_initial_state: frozenset[State] = self.epsilon_closure(
            {self.initial_state}
        )

        seen_states: dict[frozenset[State], State] = {
            dfa_initial_state: State(dfa_initial_state)
        }

        dfa: FSA = FSA(
            initial_state=seen_states[dfa_initial_state],
            states={seen_states[dfa_initial_state]},
            alphabet=set(self.alphabet),
        )

        # step 2: discover all DFA states and construct the DFA 
        # transition table 
        discovered_states: deque[frozenset[State]] = deque(
            [dfa_initial_state]
        )

        while discovered_states:
            current_dfa_state: frozenset[State] = discovered_states.popleft()

            # step 2.1: iterate over the alphabet
            for symbol in self.alphabet:
                # step 2.2: find the next DFA state using the formula:
                # δ'(Q, a) = E((∪ q∈Q) δ(q, a))
                next_dfa_state: frozenset[State] = self.epsilon_closure(
                    self.delta(current_dfa_state, symbol)
                )

                if not complete and not next_dfa_state: continue

                if next_dfa_state not in seen_states:
                    seen_states[next_dfa_state] = State(next_dfa_state)
                    dfa.states.add(seen_states[next_dfa_state])

                    # step 2.3: add the state to the queue if undiscovered
                    discovered_states.append(next_dfa_state)

                dfa.transition_table[
                    (seen_states[current_dfa_state], symbol)
                ] = {seen_states[next_dfa_state]}

        # step 3: identify the final states from the formula:
        # F' = {q | q ∈ Q' && q ∩ F != Ø}
        dfa.final_states = {
            dfa_state
            for nfa_states, dfa_state in seen_states.items()
            if nfa_states & self.final_states
        }

        return dfa
    
    @staticmethod
    def _dfa_accepts(dfa: FSA, word: str) -> bool:
        """Return True if the given DFA accepts the given word, 
        otherwise False.

        Raises:
            ValueError: If the given FSA is not a DFA.
        """
        if FSAType.DFA not in dfa.type:
            raise ValueError(
                f"Expected an FSA of type {FSAType.DFA}. "
                f"Got an FSA of type {dfa.type}."
            )

        current_state: State = dfa.initial_state

        for symbol in word:
            next_states: frozenset[State] = dfa.delta(current_state, symbol)

            # no next state so we hit a dead-end which means the word 
            # is not accepted
            if not next_states: return False

            # since we are traversing a DFA the set only has one state
            (current_state, ) = next_states

        return current_state in dfa.final_states
    
    def _states_from_set(
        self, 
        states: AbstractSet[State],
    ) -> ObservableSet[State]:
        """Create and return a set of states for the class from the given 
        set of states."""
        return ObservableSet[State](
            states,
            pre_add=lambda state: hooks.states.pre_add(
                new_state=state,
                current_states=self.states
            ),
            post_discard=lambda state: hooks.states.post_discard(
                state=state,
                current_final_states=self.final_states,
                current_transition_table=self.transition_table
            ),
            pre_discard=lambda state: hooks.states.pre_discard(
                state=state,
                current_initial_state=self.initial_state,
            )
        )

    def _final_states_from_set(
        self, 
        final_states: AbstractSet[State] | None = None
    ) -> ObservableSet[State]:
        """Create a set of final states for the class from the given set 
        of final states."""
        return ObservableSet[State](
            final_states,
            pre_add=lambda state: hooks.final_states.pre_add(
                new_final_state=state,
                current_states=self.states
            )
        )
    
    def _alphabet_from_set(
        self,
        alphabet: AbstractSet[str] | None = None
    ) -> ObservableSet[str]:
        """Create an alphabet for the class from the given set of symbols."""
        return ObservableSet[str](
            alphabet,
            pre_add=lambda symbol: hooks.alphabet.pre_add(symbol),
            post_discard=lambda symbol: hooks.alphabet.post_discard(
                symbol=symbol, 
                current_transition_table=self.transition_table
            ),
        )
    
    def _transition_table_from_set(
        self,
        transitions: AbstractSet[tuple[State, str, State]] | None = None
    ) -> TransitionTable:
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

        return TransitionTable(
            transition_data,
            pre_setitem=(
                lambda key, value: hooks.transition_table.pre_setitem(
                    key=key,
                    value=value,
                    current_states=self.states,
                    current_alphabet=self.alphabet
                )
            ),
            pre_value_add=lambda state: hooks.transition_table.pre_value_add(
                new_state=state,
                current_states=self.states
            ),
        )