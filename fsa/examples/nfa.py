from ..utils import states
from ..fsa import FSA
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..state import State

q: list[State] = states(4)
nfa: FSA = FSA(
    states=set(q),
    initial_state=q[0],
    final_states={q[3]},
    alphabet={"0", "1", "2"},
    transitions={
        (q[0], "0", q[1]),
        (q[1], "1", q[1]),
        (q[1], "1", q[2]),
        (q[1], "1", q[3]),
        (q[2], "1", q[3]),
        (q[2], "2", q[2]),
        (q[3], "0", q[2])
    }
)