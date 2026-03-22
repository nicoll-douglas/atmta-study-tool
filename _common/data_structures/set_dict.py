from typing import Iterable as TIterable, override, Mapping
from collections import UserDict
from collections.abc import Iterable


class SetDict[T, U](UserDict[frozenset[T], U]):
    """Represents a dictionary that maps sets as keys to values."""

    def __init__(self, mapping: Mapping[TIterable[T], U] | None = None):
        super().__init__({self._key(k): v for k, v in mapping.items()})

    def _key(self, iterable: TIterable[T]) -> frozenset[T]:
        """Get the underlying key in the dictionary for an iterable."""
        return frozenset(iterable)

    @override
    def __setitem__(self, key: TIterable[T], value: U) -> None:
        super().__setitem__(self._key(key), value)

    @override
    def __getitem__(self, key: TIterable[T]) -> U:
        return super().__getitem__(self._key(key))

    @override
    def __delitem__(self, key: TIterable[T]) -> None:
        super().__delitem__(self._key(key))

    @override
    def __contains__(self, item: object) -> bool:
        if not isinstance(item, Iterable):
            return False

        return super().__contains__(self._key(item))
