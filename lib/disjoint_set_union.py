from typing import Iterable, Iterator


class DisjointSetUnion[T]:
    """A Disjoint Set Union data structure with path compression to perform
    union find."""

    # mapping of states to their immediate parents
    _parents: dict[T, T]
    # all items under consideration of the data structure
    _items: Iterable[T]

    def __init__(self, items: Iterable[T]):
        """Initialise the disjoint sets with each item in its own
        disjoint set."""
        self._items = items
        self._parents = {t: t for t in items}

    def parent(self, item: T) -> T:
        """Return the immediate parent of the given item."""
        return self._parents[item]

    def find(self, item: T) -> T:
        """Find the representative (root) of the set containing 'item'.

        Implements path compression by updating the parent of all
        traversed nodes to point directly to the root.

        Args:
            item: The element to find the root for.

        Returns:
            The root representative of the set.
        """
        if self._parents[item] == item:
            return item

        self._parents[item] = self.find(self._parents[item])

        return self._parents[item]

    def union(self, item_a: T, item_b: T) -> None:
        """Merge the sets containing 'item_a' and 'item_b'.

        If the items are already in the same set, this operation
        does nothing.

        Args:
            item_a: First element.
            item_b: Second element.
        """
        root_a: T = self.find(item_a)
        root_b: T = self.find(item_b)

        if root_a != root_b:
            self._parents[root_a] = root_b

    def __iter__(self) -> Iterator[T]:
        return iter(self._items)
