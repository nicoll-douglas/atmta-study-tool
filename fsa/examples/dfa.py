from ..utils.states import states
from ..models.fsa import FSA
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models.state import State

q: list[State] = states(3)
dfa: FSA = FSA(
    states=set(q),
    initial_state=q[0],
    final_states={q[1]},
    alphabet={"a", "b"},
    transitions={
        (q[0], "b", q[1]),
        (q[1], "a", q[1]),
        (q[1], "b", q[2]),
        (q[2], "a", q[2]),
        (q[2], "b", q[1]),
    },
)
