from collections.abc import Iterator, Set


class DisjointSetUnion[T]:
    """A Disjoint Set Union data structure with path compression."""

    # mapping of states to their immediate parents
    _parents: dict[T, T]
    # all items under consideration of the data structure
    _items: Set[T]

    def __init__(self, items: Set[T]):
        """Initialise the disjoint sets with each item in its own disjoint set."""
        self._items = items
        self._parents = {t: t for t in items}

    def find(self, item: T) -> T:
        """Find the representative (root) of the set containing 'item'.

        Implements path compression by updating the parent of all traversed nodes to point directly to the root.

        Args:
            item: The element to find the root for.

        Returns:
            The root representative of the set.
        """
        parent: T = self._parents[item]

        if parent == item:
            return item

        root: T = self.find(parent)
        self._parents[item] = root

        return root

    def union(self, item_a: T, item_b: T) -> None:
        """Merge the sets containing 'item_a' and 'item_b'.

        If the items are already in the same set (i.e have the same root), this operation does nothing.

        Args:
            item_a: First element.
            item_b: Second element.
        """
        root_a: T = self.find(item_a)
        root_b: T = self.find(item_b)

        if root_a != root_b:
            self._parents[root_a] = root_b

    def sets(self) -> dict[T, set[T]]:
        groupings: dict[T, set[T]] = {}

        for item in self:
            root: T = self.find(item)

            if root not in groupings:
                groupings[root] = set()

            groupings[root].add(item)

        return groupings

    def __iter__(self) -> Iterator[T]:
        return iter(self._items)
