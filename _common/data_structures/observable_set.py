from __future__ import annotations
from collections.abc import MutableSet, Iterable, Iterator, Callable
from typing import override


class ObservableSet[T](MutableSet[T]):
    """Class that implements set observability using pre and post mutation hooks."""

    # the underlying set data
    _data: set[T]
    # hook function to run before an item is added to the set
    _pre_add: Callable[[T], None] | None
    # hook function to run after an item is added to the set
    _post_add: Callable[[T], None] | None
    # hook function to run before an item is discarded from the set
    _pre_discard: Callable[[T], None] | None
    # hook function to run after an item is discarded from the set
    _post_discard: Callable[[T], None] | None

    def __init__(
        self,
        iterable: Iterable[T] | None = None,
        pre_add: Callable[[T], None] | None = None,
        post_add: Callable[[T], None] | None = None,
        pre_discard: Callable[[T], None] | None = None,
        post_discard: Callable[[T], None] | None = None,
    ):
        self._data = set()
        self._pre_add = pre_add
        self._pre_discard = pre_discard
        self._post_add = post_add
        self._post_discard = post_discard

        if iterable:
            for element in iterable:
                self.add(element)

    def add(self, element: T) -> None:
        """Add an element to the set, running pre and post-add hooks."""
        if self._pre_add is not None:
            self._pre_add(element)

        self._data.add(element)

        if self._post_add is not None:
            self._post_add(element)

    def discard(self, element: T) -> None:
        """Discard an element from the set if it is in the set, running pre and post-add hooks."""
        if self._pre_discard is not None:
            self._pre_discard(element)

        self._data.discard(element)

        if self._post_discard is not None:
            self._post_discard(element)

    def __contains__(self, element: object) -> bool:
        return element in self._data

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[T]:
        return iter(self._data)

    @override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._data!r})"


class ObservableSetController:
    """Controller class for modifying ObservableSet internals."""

    @staticmethod
    def set__pre_add[T](
        observable_set: ObservableSet[T],
        value: Callable[[T], None] | None = None,
    ) -> None:
        observable_set._pre_add = value

    @staticmethod
    def set__post_add[T](
        observable_set: ObservableSet[T],
        value: Callable[[T], None] | None = None,
    ) -> None:
        observable_set._post_add = value

    @staticmethod
    def set__pre_discard[T](
        observable_set: ObservableSet[T],
        value: Callable[[T], None] | None = None,
    ) -> None:
        observable_set._pre_discard = value

    @staticmethod
    def set__post_discard[T](
        observable_set: ObservableSet[T],
        value: Callable[[T], None] | None = None,
    ) -> None:
        observable_set._post_discard = value
