from ..models.fsa import FSA
from ..models.state import State
from typing import Literal
from collections import deque
from .epsilon_remove import epsilon_remove


def product(
    a: FSA,
    b: FSA,
    acceptance: Literal["intersection", "union", "difference", "xor"] = "intersection",
) -> FSA:
    """Create and return the product FSA with another FSA.

    Args:
        a: The first FSA.
        b: The second FSA.
        acceptance: The strategy for computing final states. For
        intersection a product state is final if both states were
        original final states. For union, 1 or more. For difference
        the state taken from 'a' must be final but not the state
        taken from 'b'. For xor, 1 or the other.

    Returns:
        The product FSA.
    """
    a = epsilon_remove(a)
    b = epsilon_remove(b)

    # a map of tuples to actual state objects in the product FSA
    product_states: dict[tuple[State, State], State] = {
        (a_state, b_state): State((a_state, b_state))
        for a_state in a.states
        for b_state in b.states
    }

    product_initial_state: tuple[State, State] = (a.initial_state, b.initial_state)

    product_fsa: FSA = FSA(
        initial_state=product_states[product_initial_state],
        states=set(product_states.values()),
        alphabet=a.alphabet | b.alphabet,
    )

    seen_states: set[tuple[State, State]] = {product_initial_state}

    discovered: deque[tuple[State, State]] = deque([product_initial_state])

    common_symbols: set[str] = a.alphabet & b.alphabet

    while discovered:
        current: tuple[State, State] = discovered.popleft()

        for symbol in common_symbols:
            a_state: State
            b_state: State
            a_state, b_state = current

            for delta_a in a.delta(a_state, symbol):
                for delta_b in b.delta(b_state, symbol):
                    product_state: tuple[State, State] = (delta_a, delta_b)

                    product_fsa.transition_table[(product_states[current], symbol)].add(
                        product_states[product_state]
                    )

                    if product_state not in seen_states:
                        seen_states.add(product_state)
                        discovered.append(product_state)

    if acceptance == "union":
        product_fsa.final_states = {
            product_state
            for (a_state, b_state), product_state in product_states.items()
            if a_state in a.final_states or b_state in b.final_states
        }
    elif acceptance == "difference":
        product_fsa.final_states = {
            product_state
            for (a_state, b_state), product_state in product_states.items()
            if a_state in a.final_states and b_state not in b.final_states
        }
    elif acceptance == "xor":
        product_fsa.final_states = {
            product_state
            for (a_state, b_state), product_state in product_states.items()
            if (a_state in a.final_states) ^ (b_state in b.final_states)
        }
    else:
        product_fsa.final_states = {
            product_states[(self_final_state, other_final_state)]
            for self_final_state in a.final_states
            for other_final_state in b.final_states
        }

    return product_fsa
