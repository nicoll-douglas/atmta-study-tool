from __future__ import annotations
from typing import Self
from atmta_study_tool._common.data_structures import UID
from collections.abc import Callable


class State[U](UID[U]):
    """Implements a state in an automaton as a string-based UID."""

    _label: Callable[[U], str] | None

    def __new__(cls, uid: U, label: Callable[[U], str] | None = None) -> Self:
        instance: Self = super().__new__(cls, uid)
        instance._label = label

        return instance

    def __getnewargs__(self) -> tuple:
        return (self.UID, self._label)

    def __str__(self) -> str:
        return super().__str__() if self._label is None else self._label(self.UID)
