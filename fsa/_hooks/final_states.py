from typing import AbstractSet, TYPE_CHECKING

if TYPE_CHECKING:
    from ..models.state import State


# hook function run before a final state is added to the set of final states
# of an FSA
def pre_add(new_final_state: State, current_states: AbstractSet[State]) -> None:
    """Validate that the final state being added to the set of final states
    is in the given set of states."""
    if new_final_state not in current_states:
        raise ValueError(
            "Expected a state in the set of states "
            f"{current_states}. Got {new_final_state}."
        )
