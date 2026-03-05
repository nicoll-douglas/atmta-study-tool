from typing import Iterable, Iterator

class UnionFinder[T]:
    _parents: dict[T, T]
    _items: Iterable[T]

    def __init__(self, items: Iterable[T]):
        self._items = items
        self._parents = {t: t for t in items}
    
    def parent(self, item: T) -> T:
        return self._parents[item]
        
    def find(self, item: T) -> T:
        if self._parents[item] == item:
            return item
        
        self._parents[item] = self.find(self.parent(item))

        return self.parent(item)
    
    def union(self, item_a: T, item_b: T) -> None:
        root_a: T = self.find(item_a)
        root_b: T = self.find(item_b)

        if root_a != root_b:
            self._parents[root_a] = root_b

    def items(self) -> Iterator[T]:
        return iter(self._items)
