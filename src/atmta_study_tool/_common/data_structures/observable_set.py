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

    def add(self, value: T) -> None:
        """Add an element to the set, running pre and post-add hooks."""
        if self._pre_add is not None:
            self._pre_add(value)

        self._data.add(value)

        if self._post_add is not None:
            self._post_add(value)

    def discard(self, value: T) -> None:
        """Discard an element from the set if it is in the set, running pre and post-add hooks."""
        if self._pre_discard is not None:
            self._pre_discard(value)

        self._data.discard(value)

        if self._post_discard is not None:
            self._post_discard(value)

    def __contains__(self, element: object) -> bool:
        return element in self._data

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[T]:
        return iter(self._data)

    @override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._data!r})"


class ObservableSetController[T]:
    """Controller class for modifying ObservableSet internals."""

    obs_set: ObservableSet[T]

    def __init__(self, obs_set: ObservableSet[T]) -> None:
        self.obs_set = obs_set

    def set_pre_add(
        self,
        value: Callable[[T], None] | None = None,
    ) -> None:
        self.obs_set._pre_add = value

    def set_post_add(
        self,
        value: Callable[[T], None] | None = None,
    ) -> None:
        self.obs_set._post_add = value

    def set_pre_discard(
        self,
        value: Callable[[T], None] | None = None,
    ) -> None:
        self.obs_set._pre_discard = value

    def set_post_discard(
        self,
        value: Callable[[T], None] | None = None,
    ) -> None:
        self.obs_set._post_discard = value
