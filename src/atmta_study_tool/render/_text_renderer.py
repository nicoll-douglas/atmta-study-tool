from collections.abc import Iterable, Set


class TextRenderer:
    """Represents a text renderer."""

    def _get_set_str(self, items: Set[object]) -> str:
        """Get a string representing the given items as a set."""
        return "{" + ", ".join(str(item) for item in items) + "}"

    def _get_tuple_str(self, items: Iterable[object]) -> str:
        """Get a string representing the given items as a tuple."""
        return "(" + ", ".join(str(item) for item in items) + ")"
