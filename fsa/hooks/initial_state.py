from typing import TYPE_CHECKING, AbstractSet

if TYPE_CHECKING:
    from ..state import State

# hook function to run before the initial state of an FSA is set
def pre_set(
    new_initial_state: State,
    current_states: AbstractSet[State]
) -> None:
    """Validate that the new initial state is in the current set of states."""
    if new_initial_state not in current_states:
        raise ValueError(
            f"Expected a state in the set of states {current_states}. "
            f"Got {new_initial_state}."
        )