from __future__ import annotations
from atmta_study_tool._common.data_structures import UID
from atmta_study_tool._common.constants import EPSILON_UID
import unicodedata


class Symbol(UID[str]):
    def __init__(self, uid: str):
        Symbol._validate_uid(uid)
        super().__init__(uid)

    @staticmethod
    def _validate_uid(uid: str):
        if uid == EPSILON_UID:
            raise ValueError(
                f"Expected a string not equal to {EPSILON_UID!r}. Got {uid!r}."
            )

        # TODO: validate that the uid is not empty


Symbol.__doc__ = f"Implements a symbol as a string-based UID object.\n\nThe UID cannot be '{EPSILON_UID}' ({unicodedata.name(EPSILON_UID)})."
