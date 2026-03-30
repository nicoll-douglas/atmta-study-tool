from __future__ import annotations
from typing import override
from atmta_study_tool._common.data_structures import UID


class State[T: (str, frozenset["State"])](UID[T]):
    """Implements a state in an automaton as a string-based state-set-based UID."""

    @override
    def __str__(self) -> str:
        if isinstance(self.UID, str):
            return super().__str__()

        return "{" + ", ".join(str(s) for s in self.UID) + "}"
