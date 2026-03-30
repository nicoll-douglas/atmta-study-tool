from atmta_study_tool._common.data_structures import ObservableSet
from .symbol import Symbol
from collections.abc import Iterable
from typing import Self


class Alphabet(ObservableSet[Symbol]):
    """Implements an alphabet as an observable set of symbols."""

    def __init__(
        self,
        symbols: Iterable[Symbol] | None = None,
    ):
        def _validate_epsilon(symbol: Symbol):
            if symbol == Symbol.EPSILON:
                raise ValueError(
                    f"Expected a symbol not equal to epsilon. Got {symbol!r}."
                )

        super().__init__(
            symbols, pre_add=_validate_epsilon, pre_discard=_validate_epsilon
        )

    def copy(self) -> Self:
        """Create a new alphabet with the same set of symbols."""
        return self.__class__(self)
