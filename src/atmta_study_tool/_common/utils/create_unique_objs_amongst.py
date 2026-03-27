from collections.abc import Set, Callable
from typing import overload, Literal


@overload
def create_unique_objs_amongst[T](
    items: Set[T],
    initial: T,
    factory: Callable[[int], T],
    create: Literal[1] = 1,
    count_start: int = 1,
) -> T: ...


@overload
def create_unique_objs_amongst[T](
    items: Set[T],
    initial: T,
    factory: Callable[[int], T],
    create: int,
    count_start: int = 1,
) -> set[T]: ...


def create_unique_objs_amongst[T](
    items: Set[T],
    initial: T,
    factory: Callable[[int], T],
    create: int | Literal[1] = 1,
    count_start: int = 1,
) -> set[T] | T:
    unique_items: set[T] = set()

    for _ in range(create):
        counter: int = count_start
        unique: T = initial

        while unique in items | unique_items:
            unique = factory(counter)
            counter += 1

        unique_items.add(unique)

    if create == 1:
        return unique_items.pop()

    return unique_items
