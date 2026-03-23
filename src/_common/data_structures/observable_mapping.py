from __future__ import annotations
from typing import override
from collections.abc import MutableMapping, Callable, Mapping


class ObservableMapping[K, V](MutableMapping[K, V]):
    """Class that implements mapping observability using pre and post mutation hooks."""

    # the underlying data of the mapping
    _data: dict[K, V]
    # hook function to run before an item is set in the dictionary
    _pre_setitem: Callable[[K, V], None] | None
    # hook function to run after an item is set in the dictionary
    _post_setitem: Callable[[K, V], None] | None
    # hook function to run before an item is deleted from the dictionary
    _pre_delitem: Callable[[K], None] | None
    # hook function to run after an item is set in the dictionary
    _post_delitem: Callable[[K], None] | None

    def __init__(
        self,
        mapping: Mapping[K, V] | None = None,
        pre_setitem: Callable[[K, V], None] | None = None,
        post_setitem: Callable[[K, V], None] | None = None,
        pre_delitem: Callable[[K], None] | None = None,
        post_delitem: Callable[[K], None] | None = None,
        /,
        **kwargs,
    ):
        self._data = {}
        self._pre_setitem = pre_setitem
        self._post_setitem = post_setitem
        self._pre_delitem = pre_delitem
        self._post_delitem = post_delitem

        if mapping is not None:
            self.update(mapping)

        if kwargs:
            self.update(kwargs)

    def __getitem__(self, key) -> V:
        if key in self._data:
            return self._data[key]

        if hasattr(self.__class__, "__missing__"):
            return self.__class__.__missing__(self, key)

        raise KeyError(key)

    def __setitem__(self, key: K, value: V) -> None:
        """Set an item in the dictionary, running pre and post-setitem hooks."""
        if self._pre_setitem is not None:
            self._pre_setitem(key, value)

        self._data[key] = value

        if self._post_setitem is not None:
            self._post_setitem(key, value)

    def __delitem__(self, key: K) -> None:
        """Delete an item in the dictionary, running pre and post-delitem hooks."""
        if self._pre_delitem is not None:
            self._pre_delitem(key)

        del self._data[key]

        if self._post_delitem is not None:
            self._post_delitem(key)

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    @override
    def __repr__(self):
        return f"{self.__class__.__name__}({self._data!r})"

    @override
    def __contains__(self, key: object) -> bool:
        return key in self._data
