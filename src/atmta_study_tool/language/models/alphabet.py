from atmta_study_tool._common.data_structures import ObservableSet
from .symbol import Symbol
from collections.abc import Iterable


class Alphabet(ObservableSet[Symbol]):
    """Implements an alphabet as an observable set of symbols."""

    def __init__(
        self,
        symbols: Iterable[Symbol] | None = None,
    ):
        super().__init__(symbols)
