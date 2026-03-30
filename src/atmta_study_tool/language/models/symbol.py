from __future__ import annotations
from atmta_study_tool._common.data_structures import UID
from atmta_study_tool._common.constants import EPSILON_UID
from typing import Self


class Symbol(UID[str]):
    """Implements a symbol as a string-based UID object."""

    EPSILON: Symbol

    def __new__(cls, uid: str) -> Self:
        if uid == "":
            raise ValueError(f"Expected a non-empty string. Got {uid!r}.")

        return super().__new__(cls, uid)


Symbol.EPSILON = Symbol(EPSILON_UID)
