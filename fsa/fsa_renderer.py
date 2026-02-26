from graphviz import Digraph
from .fsa import FSA

class FSARenderer:
    """Represents a renderer object that can render FSA diagrams."""

    # the label used for epsilon-transitions
    EPSILON_LABEL: str = "\u03b5"

    def render(self, fsa: FSA, filename: str, open_file: bool = True) -> None:
        """Create an image representation of the given FSA and optionally 
        open the image file.

        Args:
            filename: The extension-less filename to give the .png file.
            open_file: Whether to open the .png file for immediate 
            viewing.
        """
        graph: Digraph = Digraph("FSA", format="png")

        graph.attr(rankdir="LR")

        for state in fsa.states:
            shape: str = (
                "doublecircle" 
                if state in fsa.final_states 
                else "circle"
            )

            graph.node(state.label, shape=shape)

        for (start_state, label), end_state in (
            fsa.transition_table.items()
        ):
            graph.edge(
                start_state.label, 
                end_state.label,
                label=(
                    FSARenderer.EPSILON_LABEL
                    if label == FSA.EPSILON 
                    else label
                )
            )

        graph.node("start", label="", shape="none", width="0", height="0")
        graph.edge("start", fsa.initial_state.label)
        graph.render(filename, view=open_file, cleanup=True)