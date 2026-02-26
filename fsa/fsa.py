from __future__ import annotations
from collections import deque, defaultdict
from typing import Set, Callable
from .alphabet import Alphabet
from .state import State
from .word import EPSILON
from .state_set import StateSet
from .state_subset import StateSubset
from .transition_table import TransitionTable
from .tools import subset_construction

class FSA:
    """Represents a finite-state automaton (FSA) and contains algorithms 
    that operate on it."""

    _transition_table: TransitionTable

    def __init__(
        self,
        initial_state: State,
        states: Set[State],
        alphabet: Set[str] | None = None,
        transitions: Set[tuple[State, str, State]] | None = None,
        final_states: Set[State] | None = None
    ):
        state_set_func: Callable[[TransitionTable], StateSet] = (
            lambda tt: StateSet(
                initial_state=initial_state,
                final_states=final_states,
                states=states,
                transition_table=tt
            )
        )
        alphabet_func: Callable[[TransitionTable], Alphabet] = (
            lambda tt: Alphabet(
                alphabet=alphabet,
                transition_table=tt
            )
        )

        data: defaultdict[
            TransitionTable.Key,
            Set[State]
        ] | None

        if transitions is not None:
            data = defaultdict(set)

            for start_state, letter, end_state in transitions:
                data[(start_state, letter)].add(end_state)
        else:
            data = None

        self._transition_table = TransitionTable(
            states=state_set_func,
            alphabet=alphabet_func,
            data=data
        )

    @property
    def states(self) -> StateSet:
        """Get the FSA's set of states."""
        return self._transition_table._states
    
    @property
    def initial_state(self) -> State:
        return self._transition_table._states._initial_state
    
    @initial_state.setter
    def initial_state(self, value: State) -> None:
        self._transition_table._states._initial_state = value
    
    @property
    def final_states(self) -> StateSubset:
        return self._transition_table._states._final_states
    
    @final_states.setter
    def final_states(self, value: Set[State]) -> None:
        self._transition_table._states._final_states = value
    
    @property
    def alphabet(self) -> Alphabet:
        return self._transition_table._alphabet
    
    @alphabet.setter
    def alphabet(self, value: Set[str]) -> None:
        self._transition_table._alphabet = value
    
    @property
    def transition_table(
        self
    ) -> TransitionTable:
        return self._transition_table
    
    @property
    def is_dfa(self) -> bool:
        """Return a boolean flag indicating whether the FSA is a 
        deterministic FSA (DFA) or not."""
        return all(
            label != EPSILON
            and len(end_states) <= 1
            for (_, label), end_states in self.transition_table.items()
        )
    
    @property
    def is_complete_dfa(self) -> bool:
        """Return a boolean flag indicating whether the FSA is a 
        complete DFA.

        A complete DFA must have exactly 1 outgoing transition for 
        every combination of state and letter.
        """
        return self.is_dfa and all(
            len(self.delta(state, letter)) == 1
            for letter in self.alphabet
            for state in self.states
        )

    @property
    def is_nfa(self) -> bool:
        """Return a boolean flag indicating whether the FSA is a 
        non-deterministic FSA (NFA) or not."""
        return not self.is_dfa

    @property
    def is_epsilon_nfa(self) -> bool:
        """Return a boolean flag indicating whether the FSA is an 
        epsilon-NFA or not."""
        return self.is_nfa and any(
            label == EPSILON
            for _, label in self.transition_table.keys()
        )

    @property
    def type(self) -> str:
        """Get a string description of the type of the FSA."""
        if self.is_complete_dfa: return "Complete DFA"
        if self.is_dfa: return "DFA"
        if self.is_epsilon_nfa: return "Epsilon-NFA"

        return "NFA"

    def delta(self, state: State, label: str) -> StateSubset:        
        return self.transition_table[(state, label)]

    def accepts(self, word: str) -> bool:
        """Return True if the FSA accepts the given word otherwise 
        False."""
        return FSA._dfa_accepts(subset_construction(self), word)

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
            
            for (start_state, _), end_states in (
                self.transition_table.items()
            ):
                if start_state == current_state:
                    for next_state in end_states:
                        if next_state not in visited:
                            visited.add(next_state)
                            queue.append(next_state)
                            
        return True

    def recognizes(self, language: set[str]) -> bool:
        """Return True if the FSA recognizes the given language, 
        otherwise False."""
        if not language: return self.recognizes_empty_language()

        dfa: FSA = subset_construction(self)

        return all(FSA._dfa_accepts(dfa, word) for word in language)
    
    @staticmethod
    def _dfa_accepts(dfa: FSA, word: str) -> bool:
        """Return True if the given DFA accepts the given word, 
        otherwise False.

        Raises:
            ValueError: If the given FSA is not a DFA.
        """
        if not dfa.is_dfa:
            raise ValueError(
                f"Expected a DFA. Got an FSA of type '{dfa.type}'."
            )

        current_state: State = dfa.initial_state

        for letter in word:
            next_states: StateSubset = dfa.delta(current_state, letter)

            # no next state so we hit a dead-end which means the word 
            # is not accepted
            if not next_states: return False

            # since we are traversing a DFA the set only has one state
            (current_state, ) = next_states

        return current_state in dfa.final_states