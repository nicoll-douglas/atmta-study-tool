from collections.abc import MutableSet
from typing import override, Iterable, Iterator
from abc import abstractmethod
from itertools import chain

class ValidationSet[T](MutableSet[T]):
    """Abstract base class representing a set that validates items 
    before insertion.
    """

    # the underlying set data
    _data: set[T]

    def __init__(self, iterable: Iterable[T] | None = None):
        self._data = set()

        if iterable:
            for element in iterable:
                self.add(element)

    @abstractmethod
    def validate(self, element: T) -> None:
        """Validate whether the given element is a valid element
        to insert into the set.

        Raises:
            ValueError: If the element is invalid.
        """
        pass
    
    @override
    def add(self, element: T) -> None:
        self.validate(element)
        self._data.add(element)

    @override
    def discard(self, element: T) -> None:
        self._data.discard(element)

    @override
    def __contains__(self, element: T) -> bool:
        return element in self._data

    @override
    def __len__(self) -> int:
        return len(self._data)

    @override
    def __iter__(self) -> Iterator[T]:
        return iter(self._data)

    @override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._data})"
    
    @override
    def __or__(self, other: Iterable[T]) -> ValidationSet[T]:
        return self.__class__(chain(self, other))

    @override
    def __and__(self, other: Iterable[T]) -> ValidationSet[T]:
        return self.__class__(x for x in self if x in other)

    @override
    def __sub__(self, other: Iterable[T]) -> ValidationSet[T]:
        return self.__class__(x for x in self if x not in other)

    @override
    def __xor__(self, other: Iterable[T]) -> ValidationSet[T]:
        return (self - other) | (other - self)