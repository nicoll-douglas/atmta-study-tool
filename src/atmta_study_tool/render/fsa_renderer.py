from .printer import Printer
from .transition_graph_renderer import TransitionGraphRenderer
from atmta_study_tool.fsa import FSA
from atmta_study_tool._common.utils import str_set, str_tuple


class FSARenderer(TransitionGraphRenderer[FSA], Printer):
    """Represents a renderer object that can render FSAs."""

    def formal(self) -> str:
        """Return the FSA as its formal 5-tuple definition."""
        return str_tuple(
            (
                str_set(self.fsa.alphabet),
                str_set(self.fsa.states),
                str_set({str_tuple(t) for t in self.fsa.transition_table.flatten()}),
                str_set(self.fsa.final_states),
                str(self.fsa.initial_state),
                str_set(self.fsa.final_states),
            )
        )
