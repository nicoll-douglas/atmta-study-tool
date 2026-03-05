from ..utils import states
from ..fsa import FSA
from ..word import EPSILON
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..state import State

q: list[State] = states(3)
epsilon_nfa: FSA = FSA(
    states=set(q),
    initial_state=q[0],
    final_states={q[2]},
    alphabet={"a", "b", "c"},
    transitions={
        (q[0], "a", q[0]),
        (q[0], EPSILON, q[1]),
        (q[1], EPSILON, q[1]),
        (q[1], EPSILON, q[2]),
        (q[2], "b", q[1]),
        (q[2], "c", q[2])
    }
)
