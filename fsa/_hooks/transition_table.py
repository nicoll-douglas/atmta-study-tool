from ..constants import EPSILON
from typing import AbstractSet, TYPE_CHECKING

if TYPE_CHECKING:
    from ..models.transition_table import _TransitionTable
    from ..models.state import State


# hook function to run before an item is set in the transition table of an FSA
def pre_setitem(
    key: _TransitionTable.Key,
    value: AbstractSet[State],
    current_states: AbstractSet[State],
    current_alphabet: AbstractSet[str],
) -> None:
    """Validate that the key contains a state in the given set of states and
    a symbol in given alphabet or equal to epsilon, and validate that the
    value is a subset of the given set of states."""
    start_state: State
    symbol: str
    start_state, symbol = key

    if start_state not in current_states:
        raise ValueError(
            f"Expected a start state in the set of states {current_states}. "
            f"Got {start_state}."
        )

    if symbol not in current_alphabet and symbol != EPSILON:
        raise ValueError(
            f"Expected a symbol in the alphabet {current_alphabet} or "
            f"epsilon. Got '{symbol}'."
        )

    if not value <= current_states:
        raise ValueError(
            f"Expected the set of next states to be a subset of the set of "
            f"states {current_states}. Got {value}."
        )


# hook function to run before a new state is added to a set of next states
# in the transition table of an FSA
def pre_value_add(new_state: State, current_states: AbstractSet[State]) -> None:
    """Validate that the state being added is in the given set of states."""
    if new_state not in current_states:
        raise ValueError(
            f"Expected a state in the set of states {current_states}. "
            f"Got {new_state}."
        )
