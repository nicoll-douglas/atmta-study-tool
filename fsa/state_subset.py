from utils import ValidationSet
from .state import State
from typing import override, Set
from .state_set import StateSet

class StateSubset(ValidationSet[State]):
    """Represents a subset of possible states in an FSA."""

    # The set of possible states of the FSA
    _possible_states: StateSet

    def __init__(
        self, 
        possible_states: StateSet,
        subset: Set[State] | None = None
    ):
        self._possible_states = possible_states

        super().__init__(subset)
    
    @override
    def validate(self, state: State) -> None:
        """Validate whether the given state is a valid state
        to insert into the subset of states.

        Raises:
            ValueError: If the given state is not in the set of 
            possible final states for the FSA.
        """
        if state not in self._possible_states:
            raise ValueError(
                "Expected a state in the set of possible states "
                f"{self._possible_states}. Got {state}."
            )