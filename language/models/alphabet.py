from _common.datastructures import ObservableSet
from .symbol import Symbol
from typing import Iterable


class Alphabet(ObservableSet[Symbol]):
    """Implements an alphabet as an observable set of symbols."""

    def __init__(
        self,
        iterable: Iterable[Symbol] | None = None,
    ):
        super().__init__(iterable)
