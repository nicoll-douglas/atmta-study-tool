from __future__ import annotations
from weakref import WeakValueDictionary
from typing import Any, cast, Self


class UID[T]:
    """Represents a unique identifier (UID).

    Two UID objects are equal if and only if they have equal 'uid' attributes and are of the same type. All UID objects instantiated are interned in a weakly-valued dictionary.
    """

    _REGISTRY: WeakValueDictionary[tuple[type[UID[Any]], Any], UID[Any]] = (
        WeakValueDictionary()
    )

    _uid: T

    def __new__(cls, uid: T) -> Self:
        key: tuple[type[UID[Any]], T] = (cls, uid)

        if key in UID._REGISTRY:
            return cast(Self, UID._REGISTRY[key])

        instance: Self = super().__new__(cls)
        UID._REGISTRY[key] = instance

        return instance

    def __init__(self, uid: T):
        if hasattr(self, "uid"):
            return

        self._uid = uid

    @property
    def uid(self) -> T:
        return self._uid

    def __eq__(self, other: object) -> bool:
        return self is other

    def __hash__(self) -> int:
        return hash((self.__class__, self.uid))

    def __str__(self) -> str:
        return str(self.uid)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.uid!r})"
