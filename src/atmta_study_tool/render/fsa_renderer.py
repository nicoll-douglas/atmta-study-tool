from graphviz import Digraph
from collections import defaultdict
from collections.abc import Set
from os import PathLike
from atmta_study_tool.fsa import FSA, State, TransitionTable
from ._image_renderer import ImageRenderer
from ._text_renderer import TextRenderer
from pathlib import Path


class FSARenderer(TextRenderer, ImageRenderer):
    """Represents a renderer object that can render FSA diagrams."""

    # whether to combine multiple transitions between two states into one edge
    combine_edges: bool

    def __init__(self, combine_edges: bool = True, directory: Path | str = "fsa"):
        self.combine_edges = combine_edges

        super().__init__(directory)

    def print_formal(self, fsa: FSA) -> None:
        """Print the given FSA as its formal 5-tuple definition."""
        five_tuple: str = self._get_tuple_str(
            [
                self._get_set_str(fsa.alphabet),
                self._get_set_str(fsa.states),
                # TODO: add easy way to get string representation of transitions
                self._get_set_str(fsa.final_states),
                str(fsa.initial_state),
                self._get_set_str(fsa.final_states),
            ]
        )

        print(five_tuple)

    def render_image(
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
        self._insert_nodes(graph, fsa.states, fsa.final_states)

        if self.combine_edges:
            self._insert_combined_edges(graph, fsa.transition_table)
        else:
            self._insert_edges(graph, fsa.transition_table)

        self._insert_initial_state_arrow(graph, fsa.initial_state)

        graph.render(filename, directory=self._render_dir, view=open_file, cleanup=True)

    def _insert_initial_state_arrow(self, graph: Digraph, initial_state: State) -> None:
        """Insert the arrow that points to the node of the initial state into the given graph."""
        graph.node("start", label="", shape="none", width="0", height="0")
        graph.edge("start", initial_state.UID)

    def _insert_nodes(
        self,
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

    def _insert_edges(self, graph: Digraph, transition_table: TransitionTable) -> None:
        """Insert edges into the given graph based on the given FSA transition table."""
        for (start_state, symbol), next_states in transition_table.items():
            for next_state in next_states:
                graph.edge(
                    start_state.UID,
                    next_state.UID,
                    label=str(symbol),
                )

    def _insert_combined_edges(
        self, graph: Digraph, transition_table: TransitionTable
    ) -> None:
        """Insert edges with combined transitions into the given graph for the given FSA transition table."""
        transition_labels: defaultdict[tuple[State, State], set[str]] = defaultdict(set)

        for (start_state, symbol), next_states in transition_table.items():
            for next_state in next_states:
                transition_labels[(start_state, next_state)].add(str(symbol))

        for (start_state, next_state), labels in transition_labels.items():
            graph.edge(start_state.UID, next_state.UID, label=", ".join(sorted(labels)))
