from __future__ import annotations
from .symbol import Symbol
from typing import override, SupportsIndex, overload, cast
from collections.abc import Sequence


class Word(tuple[Symbol, ...]):
    """Implements a word as a list of symbols."""

    # the empty word
    EPSILON: Word

    def __new__(cls, iterable: Sequence[Symbol] | Sequence[str] | None = None) -> Word:
        match iterable:
            case [Symbol(), *_]:
                return super().__new__(cls, iterable)
            case [str(_), *_]:
                return super().__new__(cls, (Symbol(s) for s in iterable))
            case _:
                return super().__new__(cls)

    def __repr__(self):
        return f"{self.__class__.__name__}({super().__repr__()})"

    @classmethod
    def _validate_word(cls, obj: object):
        """Validate that the given object is an instance of the class or raise a ValueError otherwise."""
        if not isinstance(obj, Word):
            raise ValueError(f"Expected an instance of {cls.__name__}. Got {obj!r}.")

    @override
    def __add__(self, other: object) -> Word:
        self._validate_word(other)
        other = cast(Word, other)

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

    # TODO: add __str__ method that returns word as string, Word.EPSILON -> epsilon character

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
