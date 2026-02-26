from typing import override, Set
from .fsa_renderer import FSARenderer
from utils import ValidationSet
from .transition_table import TransitionTable

class Alphabet(ValidationSet[str]):
    """Represent's an alphabet containing strings of length 1."""

    # a reference to a transition table associated with the alphabet
    _transition_table: TransitionTable

    def __init__(
        self, 
        transition_table: TransitionTable,
        alphabet: Set[str] | None = None,
    ):
        self._transition_table = transition_table

        super().__init__(alphabet)

    @override
    def validate(self, value: str) -> None:
        """Validate whether the given value is a valid letter to insert 
        into the alphabet.

        Raises:
            ValueError: If the length of the letter is not equal to 1 or 
            is equal to the epsilon character used by FSARenderer.
        """
        if value == FSARenderer.EPSILON_LABEL:
            raise ValueError(
                f"Expected a string not equal to "
                f"'{FSARenderer.EPSILON_LABEL}' "
                f"(U+{ord(value):04X}). Got '{value}'."
            )
        
        if len(value) != 1:
            raise ValueError(
                "Expected a string of length 1. "
                f"Got '{value}'."
            )
    
    @override
    def discard(self, letter: str) -> None:
        """Delete all transitions from the transition table that use 
        the given letter and remove the letter from the alphabet."""
        for start_state, letter in list(self._transition_table.keys()):
            if letter == letter:
                del self._transition_table[(start_state, letter)]

        super().discard(letter)