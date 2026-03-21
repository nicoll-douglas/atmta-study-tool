from __future__ import annotations
from collections import UserList
from .symbol import Symbol


class Word(UserList[Symbol]):
    """Implements a word as a list of symbols."""

    # the empty word
    EPSILON: Word

    def __repr__(self):
        return f"{self.__class__.__name__}({self.data})"


Word.EPSILON = Word()
