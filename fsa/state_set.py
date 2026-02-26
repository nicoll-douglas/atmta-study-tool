from utils import ValidationSet
from .state import State
from typing import override, Set
from .state_subset import StateSubset
from .transition_table import TransitionTable

class StateSet(ValidationSet[State]):
    """Represents a set of possible states for an FSA."""

    # The labels of all states
    _labels: set[str]
    # The initial state of the FSA
    _initial_state_raw: State
    # The final states of the FSA
    _final_states_raw: StateSubset
    # A transition table associated with the FSA
    _transition_table: TransitionTable

    def __init__(
        self, 
        initial_state: State,
        states: Set[State],
        transition_table: TransitionTable,
        final_states: Set[State] | None = None,
    ):
        self._transition_table = transition_table

        if states:
            for state in states:
                self._labels.add(state.label)
               
        super().__init__(states)

        self._initial_state = initial_state
        self._final_states = final_states

    @property
    def _initial_state(self) -> State:
        return self._initial_state_raw
    
    @_initial_state.setter
    def _initial_state(self, value: State):
        """Set the initial state of the FSA.
        
        Raises:
            ValueError: If the state is not in the set of possible 
            states for the FSA.
        """
        if value not in self:
            raise ValueError(
                f"Expected a state in the set of states {self}. "
                f"Got {value}."
            )
        
        self._initial_state_raw = value

    @property
    def _final_states(self) -> StateSubset:
        return self._final_states
    
    @_final_states.setter 
    def _final_states(self, value: Set[State]) -> None:
        self._final_states_raw = StateSubset(self, value)
        
    @override
    def validate(self, state: State) -> None:
        """Validate whether the given state is a valid state
        to insert into the set of states.

        Raises:
            ValueError: If the given state does not have a unique 
            label amongst the set of states.
        """
        if state not in self and state.label in self._labels:
            raise ValueError(
                "Expected a state with a unique label. Got "
                f"duplicate label '{state.label}'."
            )
    
    @override
    def discard(self, state: State) -> None:
        """Remove the given state from the set of states.

        The method also removes the state from the set of final states if 
        it is a final state. It also removes all outgoing and incoming 
        transitions to that state by modifying the transition table.

        Raises:
            ValueError: If the state attempting to be removed is the initial 
            state. The initial state cannot be removed, only reassigned.
        """
        if state == self._initial_state:
            raise ValueError(
                "Expected a non-initial state in the set of states "
                f"{self}. Got {self._initial_state}."
            )
        
        self._final_states.discard(state)

        for (start_state, letter), next_states in list(
            self._transition_table.items()
        ):
            if start_state == state:
                del self._transition_table[(start_state, letter)]
            else:
                next_states.discard(state)
        
        super().discard(state)