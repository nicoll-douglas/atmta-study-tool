from typing import AbstractSet, MutableSet, TYPE_CHECKING
from ..models.state import State

if TYPE_CHECKING:
    from ..models.transition_table import _TransitionTable


# hook function to run before a new state is added to the set of states of
# an FSA
def pre_add(new_state: State, current_states: AbstractSet[State]) -> None:
    """Validate that the new state being added has a unique label amongst
    the given set of states."""
    if not State.label_is_unique(new_state, current_states):
        raise ValueError(
            f"Expected a state with a unique label amongst {current_states}."
            f" Got duplicate label '{new_state.label}'."
        )


# hook function to run before a state is discarded from the set of states
# of an FSA
def pre_discard(
    state: State,
    current_initial_state: State,
) -> None:
    """Validate that the state being removed is not the given initial
    state."""
    if state == current_initial_state:
        raise ValueError(f"Expected a non-initial state. Got initial state {state}.")


# hook function to run after a state is discarded from the set of states
# of an FSA
def post_discard(
    state: State,
    current_final_states: MutableSet[State],
    current_transition_table: _TransitionTable,
) -> None:
    """Remove the state from the given set of final states (if final) and
    remove all transitions from the given transition table that involve the
    state."""
    current_final_states.discard(state)

    current_transition_table.remove_such_that(
        lambda start_state, _, __: start_state == state
    )

    current_transition_table.for_each(
        lambda _, __, next_states: next_states.discard(state)
    )


# hook function to run before the set of states of an FSA is set
def pre_set(new_states: AbstractSet[State], current_initial_state: State) -> None:
    """Validate that set of states being set contains the given initial
    state."""
    if current_initial_state not in new_states:
        raise ValueError(
            "Expected a set of states containing the initial state "
            f"{current_initial_state}. Got {new_states}."
        )
