from __future__ import annotations
from atmta_study_tool._common.data_structures import UID
from ..constants import _EPSILON_UID  # TODO: change import to _common.constants
import unicodedata


class Symbol(UID[str]):
    def __init__(self, uid: str):
        Symbol._validate_uid(uid)
        super().__init__(uid)

    @staticmethod
    def _validate_uid(uid: str):
        if uid == _EPSILON_UID:
            raise ValueError(
                f"Expected a string not equal to {_EPSILON_UID!r}. Got {uid!r}."
            )


Symbol.__doc__ = f"Implements a symbol as a string-based UID object.\n\nThe UID cannot be {_EPSILON_UID} ({unicodedata.name(_EPSILON_UID)})."
