import pytest
from fsa.models.state import State
from fsa.models.transition_table import TransitionTable
from language.models.symbol import Symbol
from language.models.word import Word
from collections.abc import Callable
from .types import TransitionCountData


@pytest.fixture
def make_states() -> Callable[[int], tuple[State, ...]]:
    def _factory(num_states: int) -> tuple[State, ...]:
        return tuple(State(f"q{i}") for i in range(num_states))

    return _factory


@pytest.fixture
def make_symbols() -> Callable[[int], tuple[Symbol, ...]]:
    def _factory(num_symbols: int) -> tuple[Symbol, ...]:
        return tuple(Symbol(f"q{i}") for i in range(num_symbols))

    return _factory


@pytest.fixture
def transition_table_states(
    make_states: Callable[[int], tuple[State, ...]],
) -> tuple[State, ...]:
    return make_states(4)


@pytest.fixture
def transition_table_symbols(
    make_symbols: Callable[[int], tuple[Symbol, ...]],
) -> tuple[tuple[Symbol, ...], Word]:
    return (make_symbols(3), Word.EPSILON)


@pytest.fixture
def transition_table(
    transition_table_states: tuple[State, ...],
    transition_table_symbols: tuple[tuple[Symbol, ...], Word],
) -> TransitionTable:
    q: tuple[State, ...] = transition_table_states
    s, epsilon = transition_table_symbols

    table: TransitionTable = TransitionTable(
        {
            (q[0], s[0]): {q[1]},
            (q[1], s[0]): {q[1]},
            (q[1], s[1]): {q[1], q[2]},
            (q[2], s[0]): {q[2]},
            (q[2], s[2]): {q[1], q[3]},
            (q[3], s[1]): {q[0]},
            (q[3], epsilon): {q[3]},
        }
    )

    return table


@pytest.fixture
def transition_table_counts(
    transition_table_states: tuple[State, ...],
    transition_table_symbols: tuple[tuple[Symbol, ...], Word],
) -> TransitionCountData:
    q: tuple[State, ...] = transition_table_states
    s, epsilon = transition_table_symbols

    # correct to the best of my observation
    return (
        {
            q[0]: {
                "incoming": 1,
                "outgoing": 1,
                "loop": 0,
            },
            q[1]: {
                "incoming": 2,
                "outgoing": 1,
                "loop": 2,
            },
            q[2]: {
                "incoming": 1,
                "outgoing": 2,
                "loop": 1,
            },
            q[3]: {
                "incoming": 1,
                "outgoing": 1,
                "loop": 1,
            },
        },
        {s[0]: 3, s[1]: 3, s[2]: 2, epsilon: 1},
    )


@pytest.fixture
def non_epsilon_word() -> Word:
    return Word([Symbol("W"), Symbol("O"), Symbol("R"), Symbol("D")])
