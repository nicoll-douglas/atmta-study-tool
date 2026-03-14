from collections.abc import MutableSet
from typing import override, Iterable, Iterator, Callable


class ObservableSet[T](MutableSet[T]):
    """Class that implements set observability using pre and
    post mutation hooks.
    """

    # a hook function
    type Hook[U] = Callable[[U], None]

    # the underlying set data
    _data: set[T]
    # hook function to run before an item is add to the set
    _pre_add: Hook | None
    # hook function to run before an item is discarded from the set
    _pre_discard: Hook | None
    # hook function to run after an item is added to the set
    _post_add: Hook | None
    # hook function to run after an item is discarded from the set
    _post_discard: Hook | None

    def __init__(
        self,
        iterable: Iterable[T] | None = None,
        pre_add: Hook[T] | None = None,
        pre_discard: Hook[T] | None = None,
        post_add: Hook[T] | None = None,
        post_discard: Hook[T] | None = None,
    ):
        self._data = set()
        self._pre_add = pre_add
        self._pre_discard = pre_discard
        self._post_add = post_add
        self._post_discard = post_discard

        if iterable:
            for element in iterable:
                self.add(element)

    @override
    def add(self, element: T) -> None:
        """Add an element to the set, running pre and post-add hooks."""
        if self._pre_add is not None:
            self._pre_add(element)

        self._data.add(element)

        if self._post_add is not None:
            self._post_add(element)

    @override
    def discard(self, element: T) -> None:
        """Discard an element from the set if it is in the set, running
        pre and post-add hooks."""
        if self._pre_discard is not None:
            self._pre_discard(element)

        self._data.discard(element)

        if self._post_discard is not None:
            self._post_discard(element)

    @override
    def __contains__(self, element: object) -> bool:
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
    def __sub__(self, other: Iterable) -> set[T]:
        return self._data - set(other)

    @override
    def __or__(self, other: Iterable) -> set[T]:
        return self._data | set(other)

    @override
    def __and__(self, other: Iterable) -> set[T]:
        return self._data & set(other)

    @override
    def __xor__(self, other: Iterable) -> set[T]:
        return self._data ^ set(other)
