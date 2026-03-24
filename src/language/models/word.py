from __future__ import annotations
from .symbol import Symbol
from typing import override, SupportsIndex, overload


class Word(tuple[Symbol]):
    """Implements a word as a list of symbols."""

    # the empty word
    EPSILON: Word

    def __repr__(self):
        return f"{self.__class__.__name__}({super().__repr__()})"

    @override
    def __add__(self, other):
        return Word(super().__add__(other))

    @override
    def __mul__(self, other):
        return Word(super().__mul__(other))

    @overload
    def __getitem__(self, index: SupportsIndex) -> Symbol: ...

    @overload
    def __getitem__(self, index: slice) -> Word: ...

    @override
    def __getitem__(self, index: SupportsIndex | slice) -> Symbol | Word:
        item: Symbol | tuple[Symbol, ...] = super().__getitem__(index)

        if isinstance(item, tuple):
            return Word(item)

        return item

    def __eq__(self, value):
        return isinstance(value, Word) and super().__eq__(value)

    def __hash__(self):
        return hash((self.__class__, tuple(self)))

    @override
    def __contains__(self, item: object):
        if not isinstance(item, Symbol):
            return False

        return super().__contains__(item)


Word.EPSILON = Word()
