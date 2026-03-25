from typing import override
from collections import UserDict
from collections.abc import Mapping, Collection


class SetDict[T, U](UserDict[frozenset[T], U]):
    """Represents a dictionary that maps sets as keys to values."""

    def __init__(self, mapping: Mapping[Collection[T], U] | None = None):
        super().__init__(
            {self._key(k): v for k, v in mapping.items()}
            if mapping is not None
            else None
        )

    def _key(self, collection: Collection[T]) -> frozenset[T]:
        """Get the underlying key in the dictionary for a collection."""
        return frozenset(collection)

    @override
    def __setitem__(self, key: Collection[T], value: U) -> None:
        super().__setitem__(self._key(key), value)

    @override
    def __getitem__(self, key: Collection[T]) -> U:
        return super().__getitem__(self._key(key))

    @override
    def __delitem__(self, key: Collection[T]) -> None:
        super().__delitem__(self._key(key))

    @override
    def __contains__(self, item: object) -> bool:
        if not isinstance(item, Collection):
            return False

        return super().__contains__(self._key(item))
