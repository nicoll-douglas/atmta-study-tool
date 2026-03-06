from typing import Iterable, override
from collections.abc import Iterable

class SetMap[T, U](dict[frozenset[T], U]):
    """Represents a dictionary that maps sets as keys to values."""
    def __init__(
        self, 
        data: Iterable[tuple[Iterable[T], U]] | None = None
    ):
        super().__init__()

        if data is not None:
            for key, value in data:
                self[key] = value
        
    def _key(self, iterable: Iterable[T]) -> frozenset[T]:
        """Get the underlying key in the dictionary for an iterable."""
        return frozenset(iterable)
        
    @override
    def __setitem__(self, key: Iterable[T], value: U) -> None:
        super().__setitem__(self._key(key), value)
    
    @override
    def __getitem__(self, key: Iterable[T]) -> U:
        return super().__getitem__(self._key(key))
    
    @override
    def __contains__(self, item: object) -> bool:
        if not isinstance(item, Iterable):
            return False
        
        return super().__contains__(self._key(item))