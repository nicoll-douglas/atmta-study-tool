from ..fsa_renderer import FSARenderer
from typing import AbstractSet, TYPE_CHECKING

if TYPE_CHECKING:
    from ..transition_table import TransitionTable

# hook function to run before a symbol is added to the alphabet of an FSA
def pre_add(new_symbol: str) -> None:
    """Validate that the new symbol being added to an alphabet is valid."""
    if new_symbol == FSARenderer.EPSILON_LABEL:
        raise ValueError(
            f"Expected a string not equal to "
            f"'{FSARenderer.EPSILON_LABEL}' "
            f"(U+{ord(FSARenderer.EPSILON_LABEL):04X}). Got '{new_symbol}'."
        )
    
    if len(new_symbol) != 1:
        raise ValueError(
            "Expected a string of length 1. "
            f"Got '{new_symbol}'."
        )

# hook function to run after a symbol is removed from the alphabet of an FSA
def post_discard(
    symbol: str, 
    current_transition_table: TransitionTable
) -> None:
    """Remove all transitions from the given transition table if they 
    utilise the symbol removed from the alphabet."""
    current_transition_table.remove_such_that(
        lambda _, transition_symbol, __: symbol == transition_symbol
    )

# hook function to run after an alphabet is set for an FSA
def post_set(
    new_alphabet: AbstractSet[str],
    current_transition_table: TransitionTable
) -> None:
    """Remove all transitions from the given transition table if they 
    don't utilise any symbol in the new alphabet."""
    current_transition_table.remove_such_that(
        lambda _, symbol, __: symbol not in new_alphabet 
    )