from atmta_study_tool.language import Word
from collections.abc import Set, Iterable, Iterator
from collections.abc import Set, Callable
from typing import overload, Literal
from collections.abc import Iterable
from typing import Any


def guess_item_type(iterable: Iterable[Any]) -> type | None:
    """Guess and return the type of items in an iterable or None if empty."""
    if not iterable:
        return None

    return type(next(iter(iterable)))


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


def strings_from(iterable: Iterable) -> Iterator:
    return (str(item) for item in iterable)


def str_set(items: Set) -> str:
    return "{" + ", ".join(strings_from(items)) + "}"


def str_tuple(items: tuple) -> str:
    return "(" + ", ".join(strings_from(items)) + ")"


def str_list(items: list) -> str:
    return "[" + ", ".join(strings_from(items)) + "]"


def validate_epsilon(word: Word):
    """Validate the given word is equalt to the empty word epsilon."""
    if word != Word.EPSILON:
        raise ValueError(f"Expected a word equal to epsilon. Got {word!r}.")
