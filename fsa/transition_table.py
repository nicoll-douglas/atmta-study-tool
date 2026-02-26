from __future__ import annotations
from .state import State
from .alphabet import Alphabet
from .state_set import StateSet
from .state_subset import StateSubset
from .word import EPSILON
from typing import override, Mapping, Callable, Set

class TransitionTable(dict):
    """Represents the transition table for an FSA."""

    # The set of possible states for the FSA
    _states_raw: StateSet
    # The alphabet of the FSA
    _alphabet_raw: Alphabet

    type Key = tuple[State, str]
    type Value = StateSubset

    def __init__(
        self, 
        states: Callable[[TransitionTable], StateSet],
        alphabet: Callable[[TransitionTable], Alphabet], 
        data: Mapping[Key, Set[State]] | None = None,
        /,
        **kwargs
    ):
        """Initialise the transition table with the given states, 
        alphabet, and data.

        Args:
            states: A function that creates a StateSet object and gets passed 
            the current instance in order for the StateSet object to perform 
            automatic updates to the table when states change.

            alphabet: A function that creates an Alphabet object and gets 
            passed the current instance in order for the Alphabet object to 
            perform automatic updates to the table when the alphabet changes.

            data: Mapping data to add to the transition table. All and keys 
            and values must be valid according to the states and alphabet.
        """
        super().__init__()

        self._states_raw = states(self)
        self._alphabet_raw = alphabet(self)

        if data is not None:
            self.update(data)
        
        if kwargs:
            self.update(kwargs)
    
    @property
    def _alphabet(self) -> Alphabet:
        return self._alphabet_raw
    
    @_alphabet.setter
    def _alphabet(self, value: Set[str]) -> None:
        """Set the alphabet of the FSA / transition table.

        The method removes all transitions utilising letters not in 
        the new alphabet.
        """
        new_alphabet: Alphabet = Alphabet(
            transition_table=self,
            alphabet=value
        )

        for start_state, letter in list(self.keys()):
            if letter not in new_alphabet:
                del self[(start_state, letter)]

        self._alphabet = new_alphabet
    
    @property
    def _states(self) -> StateSet:
        return self._states_raw
    
    def _validate_key(self, key: Key) -> None:
        """Validate a key of the transition table dictionary.

        Raises:
            ValueError: If the key tuple contains a state not in the 
            current set of states, or a label not in the alphabet not 
            equal to epsilon.
        """
        state: State
        label: str
        state, label = key

        if state not in self._states:
            raise ValueError(
                f"Expected a state in the set of states {self._states}. "
                f"Got {state}."
            )
        
        if label not in self._alphabet and label != EPSILON:
            raise ValueError(
                f"Expected a letter in the alphabet {self._alphabet} or "
                f"epsilon. Got '{label}'."
            )
    
    @override
    def __setitem__(self, key: Key, value: set[State]):
        self._validate_key(key)

        return super().__setitem__(key, StateSubset(value))
    
    def __missing__(self, key: Key) -> Value:
        """If the key is a valid key, return an empty set indicating 
        no end states for that transition."""
        self._validate_key(key)

        return StateSubset(
            possible_states=self._states
        )
