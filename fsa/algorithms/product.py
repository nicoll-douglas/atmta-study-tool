from __future__ import annotations
from ..models.fsa import FSA
from ..models.state import State
from typing import Literal, TYPE_CHECKING
from collections import deque
from .epsilon_remove import epsilon_remove

if TYPE_CHECKING:
    from language.models import Alphabet

# represents an acceptance strategy for whether a product FSA state should be a final state
type _FinalStateAcceptanceStrategy = Literal[
    "intersection", "union", "difference", "xor"
]


class _ProductFSAState:
    """Represents a state in the new product FSA being computed."""

    # a state sourced from the first FSA (left side of the product)
    _state_a: State
    # a state sourced from the second FSA (right side of the product)
    _state_b: State
    # the actual state object that will be given to the new product FSA
    _state_obj: State

    def __init__(self, state_a: State, state_b: State):
        self._state_a = state_a
        self._state_b = state_b
        self._state_obj = _ProductFSAState._create_state_obj(state_a, state_b)

    @property
    def STATE_A(self) -> State:
        return self._state_a

    @property
    def STATE_B(self) -> State:
        return self._state_b

    @property
    def STATE_OBJ(self) -> State:
        return self._state_obj

    @staticmethod
    def _create_state_obj(state_a: State, state_b: State) -> State:
        """Create and return a state object in the new product FSA."""
        return State(f"({str(state_a)}, {str(state_b)})")

    @staticmethod
    def get_product_fsa_states(fsa_a: FSA, fsa_b: FSA) -> set[State]:
        """Get the set of states (state objects) for the new product FSA."""
        return {
            _ProductFSAState._create_state_obj(state_a, state_b)
            for state_a in fsa_a.states
            for state_b in fsa_b.states
        }

    @staticmethod
    def get_product_fsa_initial_state(fsa_a: FSA, fsa_b: FSA) -> _ProductFSAState:
        """Get the product FSA initial state."""
        return _ProductFSAState(fsa_a.initial_state, fsa_b.initial_state)

    def is_final(
        self, fsa_a: FSA, fsa_b: FSA, acceptance_strategy: _FinalStateAcceptanceStrategy
    ) -> bool:
        """Return True if the the product FSA state is a final state based on the given acceptance strategy."""
        if acceptance_strategy == "union":
            return (
                self.STATE_A in fsa_a.final_states or self.STATE_B in fsa_b.final_states
            )
        elif acceptance_strategy == "difference":
            return (
                self.STATE_A in fsa_a.final_states
                and self.STATE_B not in fsa_b.final_states
            )
        elif acceptance_strategy == "xor":
            return (self.STATE_A in fsa_a.final_states) ^ (
                self.STATE_B in fsa_b.final_states
            )
        else:
            return (
                self.STATE_A in fsa_a.final_states
                and self.STATE_B in fsa_b.final_states
            )


def product(
    a: FSA,
    b: FSA,
    acceptance_strategy: _FinalStateAcceptanceStrategy = "intersection",
    no_unreachable: bool = True,
) -> FSA:
    """Create and return the product FSA of two FSAs.

    Args:
        a: The first FSA.
        b: The second FSA.
        acceptance_strategy: The strategy for computing final states.
    """
    # remove epsilon transitions to make life easier
    a = epsilon_remove(a)
    b = epsilon_remove(b)

    product_initial_state: _ProductFSAState = (
        _ProductFSAState.get_product_fsa_initial_state(a, b)
    )

    product_fsa: FSA = FSA(
        initial_state=product_initial_state.STATE_OBJ,
        states=_ProductFSAState.get_product_fsa_states(a, b),
        alphabet=Alphabet(a.alphabet | b.alphabet),
        final_states=(
            {product_initial_state.STATE_OBJ}
            if product_initial_state.is_final(a, b, acceptance_strategy)
            else None
        ),
    )

    seen_states: set[State] = {product_initial_state.STATE_OBJ}
    states_unprocessed: deque[_ProductFSAState] = deque([product_initial_state])
    common_alphabet: Alphabet = Alphabet(a.alphabet & b.alphabet)

    while states_unprocessed:
        current_state: _ProductFSAState = states_unprocessed.popleft()

        # traverse the FSAs in parallel
        for symbol in common_alphabet:
            for a_delta in a.delta(current_state.STATE_A, symbol):
                for b_delta in b.delta(current_state.STATE_B, symbol):
                    # get a possible delta in the product FSA for the current state
                    discovered_state: _ProductFSAState = _ProductFSAState(
                        a_delta, b_delta
                    )

                    # add the delta to the transition table
                    product_fsa.transition_table[(current_state.STATE_OBJ, symbol)].add(
                        discovered_state.STATE_OBJ
                    )

                    if discovered_state.STATE_OBJ not in seen_states:
                        seen_states.add(discovered_state.STATE_OBJ)
                        states_unprocessed.append(discovered_state)

                        # final state check
                        if discovered_state.is_final(a, b, acceptance_strategy):
                            product_fsa.final_states.add(discovered_state.STATE_OBJ)

    if no_unreachable:
        product_fsa.remove_unreachable_states()

    return product_fsa
