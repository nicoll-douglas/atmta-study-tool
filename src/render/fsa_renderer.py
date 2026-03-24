from graphviz import Digraph
from collections import defaultdict
from collections.abc import Set
from os import PathLike
from .constants import _DEFAULT_RENDER_DIR, _GREEK_SMALL_LETTER_EPSILON
from language import Word, Symbol
from fsa import FSA, State, TransitionTable


class FSARenderer:
    """Represents a renderer object that can render FSA diagrams."""

    # whether to combine multiple transitions between two states into one edge
    combine_edges: bool
    # the output directory where rendered images should go
    directory: PathLike | str

    def __init__(
        self,
        combine_edges: bool = True,
        directory: PathLike | str = _DEFAULT_RENDER_DIR,
    ):
        self.combine_edges = combine_edges
        self.directory = directory

    def render(
        self, fsa: FSA, filename: PathLike | str, open_file: bool = False
    ) -> None:
        """Create an image representation (.png) of the given FSA and optionally
        open the image file.

        Args:
            filename: The filename to give the .png file.
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

        graph.render(filename, directory=self.directory, view=open_file, cleanup=True)

    @classmethod
    def _transition_label(cls, symbol: Symbol | Word) -> str:
        """Get the label of a transition in the FSA diagram based on the given transition symbol."""
        if isinstance(symbol, Word):
            return _GREEK_SMALL_LETTER_EPSILON

        if symbol.UID == _GREEK_SMALL_LETTER_EPSILON:
            return f"'{_GREEK_SMALL_LETTER_EPSILON}'"

        return symbol.UID

    @staticmethod
    def _insert_initial_state_arrow(graph: Digraph, initial_state: State) -> None:
        """Insert the arrow that points to the node of the initial state into the given graph."""
        graph.node("start", label="", shape="none", width="0", height="0")
        graph.edge("start", initial_state.UID)

    @staticmethod
    def _insert_nodes(
        graph: Digraph,
        states: Set[State],
        final_states: Set[State],
    ) -> None:
        """Insert nodes into the graph based on the given states and final states of an FSA."""
        for state in states:
            graph.node(
                state.UID,
                shape=("doublecircle" if state in final_states else "circle"),
            )

    @classmethod
    def _insert_edges(cls, graph: Digraph, transition_table: TransitionTable) -> None:
        """Insert edges into the given graph based on the given FSA transition table."""
        for (start_state, symbol), next_states in transition_table.items():
            for next_state in next_states:
                graph.edge(
                    start_state.UID,
                    next_state.UID,
                    label=cls._transition_label(symbol),
                )

    @classmethod
    def _insert_combined_edges(
        cls, graph: Digraph, transition_table: TransitionTable
    ) -> None:
        """Insert edges with combined transitions into the given graph for the given FSA transition table."""
        transition_labels: defaultdict[tuple[State, State], set[str]] = defaultdict(set)

        for (start_state, symbol), next_states in transition_table.items():
            for next_state in next_states:
                transition_labels[(start_state, next_state)].add(
                    cls._transition_label(symbol)
                )

        for (start_state, next_state), labels in transition_labels.items():
            graph.edge(start_state.UID, next_state.UID, label=", ".join(sorted(labels)))
