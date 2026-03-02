from graphviz import Digraph
from collections import defaultdict
from .word import EPSILON
from typing import TYPE_CHECKING, AbstractSet
from utils import sorted_comma_sep_string

if TYPE_CHECKING:
    from .fsa import FSA
    from .state import State
    from .transition_table import TransitionTable
    
class FSARenderer:
    """Represents a renderer object that can render FSA diagrams."""

    # the label used for epsilon-transitions
    EPSILON_LABEL: str = "\u03b5"

    # whether to combine multiple transitions between two states into 
    # one edge
    combine_edges: bool

    def __init__(self, combine_edges: bool = True):
        self.combine_edges = combine_edges

    def render(self, fsa: FSA, filename: str, open_file: bool = True) -> None:
        """Create an image representation (.png) of the given FSA and optionally 
        open the image file.

        Args:
            filename: The extension-less filename to give the .png file.
            open_file: Whether to open the .png file for immediate 
            viewing.
        """
        graph: Digraph = Digraph("FSA", format="png")

        graph.attr(rankdir="LR")
        FSARenderer._insert_nodes(graph, fsa.states, fsa.final_states)

        if self.combine_edges:
            FSARenderer._insert_combined_edges(graph, fsa.transition_table)
        else:
            FSARenderer._insert_edges(graph, fsa.transition_table)

        FSARenderer._insert_initial_state_arrow(graph, fsa.initial_state)

        graph.render(filename, view=open_file, cleanup=True)
    
    @classmethod
    def _get_diagram_transition_label(cls, symbol: str) -> str:
        """Get the label of a transition in the FSA diagram based on the 
        given transition symbol."""
        return cls.EPSILON_LABEL if symbol == EPSILON else symbol

    @staticmethod
    def _insert_initial_state_arrow(
        graph: Digraph,
        initial_state: State
    ) -> None:
        """Insert the arrow that points to the node of the initial state 
        into the given graph."""
        graph.node("start", label="", shape="none", width="0", height="0")
        graph.edge("start", initial_state.label)

    
    @staticmethod
    def _insert_nodes(
        graph: Digraph,
        states: AbstractSet[State],
        final_states: AbstractSet[State],
    ) -> None:
        """Insert nodes into the graph based on the given states and final 
        states of an FSA."""
        for state in states:
            graph.node(state.label, shape=(
                "doublecircle" 
                if state in final_states 
                else "circle"
            ))
    
    @classmethod
    def _insert_edges(
        cls,
        graph: Digraph, 
        transition_table: TransitionTable
    ) -> None:
        """Insert edges into the given graph based on the given FSA 
        transition table."""
        def _insert(
            start_state: State,
            symbol: str,
            next_states: TransitionTable.Value
        ) -> None:
            for next_state in next_states:
                graph.edge(
                    start_state.label, 
                    next_state.label,
                    label=cls._get_diagram_transition_label(symbol)
                )
            
            transition_table.for_each(_insert)

    @classmethod
    def _insert_combined_edges(
        cls,
        graph: Digraph, 
        transition_table: TransitionTable
    ) -> None:
        """Insert edges with combined transitions into the given graph for 
        the given FSA transition table."""
        transition_labels: defaultdict[
            tuple[State, State], 
            set[str]
        ] = defaultdict(set)

        def _get_combined_transition_labels(
            start_state: State, 
            symbol: str, 
            next_states: TransitionTable.Value
        ) -> None:
            for next_state in next_states:
                transition_labels[(start_state, next_state)].add(
                    cls._get_diagram_transition_label(symbol)
                )

        transition_table.for_each(_get_combined_transition_labels)

        for (start_state, next_state), labels in transition_labels.items():
            graph.edge(
                start_state.label,
                next_state.label,
                label=sorted_comma_sep_string(labels)
            )