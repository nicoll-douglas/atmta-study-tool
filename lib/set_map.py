from typing import Iterable

class SetMap[T, U](dict[frozenset[T], U]):
    def __init__(
        self, 
        data: Iterable[tuple[Iterable[T], U]] | None = None
    ):
        if data is not None:
            for key, value in data:
                self[key] = value
        
    def key(self, iterable: Iterable[T]) -> frozenset[T]:
        return frozenset(iterable)
        
    def __setitem__(
        self,
        key: Iterable[T],
        value: U
    ) -> None:
        super().__setitem__(self.key(key), value)
    
    def __getitem__(
        self,
        key: Iterable[T]
    ) -> U:
        return super().__getitem__(self.key(key))