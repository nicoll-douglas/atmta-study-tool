from collections.abc import Set, Callable


def create_unique_objs_amongst[T](
    items: Set[T], initial: T, factory: Callable[[int], T], create: int = 1
) -> set[T]:
    unique_items: set[T] = set()

    for _ in range(create):
        counter: int = 1
        unique: T = initial

        while unique in items | unique_items:
            unique = factory(counter)
            counter += 1

        unique_items.add(unique)

    return unique_items
