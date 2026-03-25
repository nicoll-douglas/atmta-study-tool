import pytest
from atmta_study_tool.fsa.models import FSA, State, TransitionTable
from atmta_study_tool.language.models import Alphabet, Symbol, Word
from collections.abc import Callable, Set
from atmta_study_tool._common.utils import create_unique_objs_amongst

# TODO: docstrings
# TODO: more tests


@pytest.fixture
def valid_fsa(
    make_states: Callable[[int], tuple[State, ...]],
    make_symbols: Callable[[int], tuple[Symbol, ...]],
) -> FSA:
    q: tuple[State, ...] = make_states(5)
    s: tuple[Symbol, ...] = make_symbols(3)

    return FSA(
        initial_state=q[0],
        alphabet=Alphabet(s),
        states=set(q),
        final_states={q[2], q[4]},
        transition_table=TransitionTable(
            {
                (q[0], s[0]): {q[1]},
                (q[0], s[2]): {q[2]},
                (q[1], s[1]): {q[2], q[3]},
                (q[1], s[2]): {q[4]},
                (q[2], s[0]): {q[2]},
            }
        ),
    )


@pytest.fixture
def valid_fsa_non_initial_state(valid_fsa: FSA) -> State:
    return next(state for state in valid_fsa.states if state != valid_fsa.initial_state)


@pytest.fixture
def valid_fsa_non_final_state(valid_fsa: FSA) -> State:
    return next(state for state in valid_fsa.states - valid_fsa.final_states)


@pytest.fixture
def valid_fsa_final_state(valid_fsa: FSA) -> State:
    return next(state for state in valid_fsa.final_states)


@pytest.fixture
def valid_fsa_state(valid_fsa: FSA) -> State:
    return next(state for state in valid_fsa.states)


@pytest.fixture
def valid_fsa_state_with_loop(valid_fsa: FSA) -> State:
    return next(
        start_state
        for (start_state, _), next_states in valid_fsa.transition_table.items()
        if start_state in next_states
    )


@pytest.fixture
def valid_fsa_symbol(valid_fsa: FSA) -> Symbol:
    return next(s for s in valid_fsa.alphabet)


@pytest.fixture
def state_not_in_valid_fsa(valid_fsa: FSA) -> State:
    return create_unique_objs_amongst(
        valid_fsa.states,
        factory=lambda counter: State(f"{counter}"),
        initial=State(""),
    )


@pytest.fixture
def symbol_not_in_valid_fsa(valid_fsa: FSA) -> Symbol:
    return create_unique_objs_amongst(
        valid_fsa.alphabet,
        factory=lambda counter: Symbol(f"{counter}"),
        initial=Symbol(""),
    )


class TestFSA:
    def test_set_initial_state(
        self, valid_fsa: FSA, valid_fsa_non_initial_state: State
    ):
        valid_fsa.initial_state = valid_fsa_non_initial_state

        assert valid_fsa.initial_state == valid_fsa_non_initial_state

    def test_set_initial_state_not_in_states(
        self, valid_fsa: FSA, state_not_in_valid_fsa: State
    ):
        with pytest.raises(ValueError):
            valid_fsa.initial_state = state_not_in_valid_fsa

    def test_add_final_state_not_in_states(
        self, valid_fsa: FSA, state_not_in_valid_fsa: State
    ):
        with pytest.raises(ValueError):
            valid_fsa.final_states.add(state_not_in_valid_fsa)

    def test_set_final_states_not_subset_of_states(
        self, valid_fsa: FSA, state_not_in_valid_fsa: State
    ):
        with pytest.raises(ValueError):
            valid_fsa.final_states = valid_fsa.final_states | {state_not_in_valid_fsa}

    def test_set_no_final_states(self, valid_fsa: FSA):
        valid_fsa.final_states = set()

        assert not valid_fsa.final_states

    def test_set_final_states(self, valid_fsa: FSA, valid_fsa_non_final_state: State):
        new_final_states: set[State] = {valid_fsa_non_final_state}

        valid_fsa.final_states = new_final_states

        assert valid_fsa.final_states == new_final_states

    def test_set_states(self, valid_fsa: FSA):
        new_states: Set[State] = (valid_fsa.states - valid_fsa.final_states) | {
            valid_fsa.initial_state
        }

        valid_fsa.states = new_states

        assert valid_fsa.states == new_states

    def test_set_states_without_initial_state(self, valid_fsa: FSA):
        with pytest.raises(ValueError):
            valid_fsa.states = valid_fsa.states - {valid_fsa.initial_state}

    def test_set_states_discards_final_states(self, valid_fsa: FSA):
        non_final_states: Set[State] = valid_fsa.states - valid_fsa.final_states

        valid_fsa.states = non_final_states

        assert not valid_fsa.final_states

    def test_discard_initial_state(self, valid_fsa: FSA):
        with pytest.raises(ValueError):
            valid_fsa.states.discard(valid_fsa.initial_state)

    def test_discard_state_discards_final_state(
        self, valid_fsa: FSA, valid_fsa_final_state: State
    ):
        valid_fsa.states.discard(valid_fsa_final_state)

        assert valid_fsa_final_state not in valid_fsa.final_states

    def test_set_states_discard_transitions(
        self, valid_fsa: FSA, valid_fsa_state_with_loop: State
    ):
        transition_remove_count: int = valid_fsa.transition_table.transition_count(
            valid_fsa_state_with_loop
        )
        total_transitions: int = valid_fsa.transition_table.transition_count()

        valid_fsa.states = valid_fsa.states - {valid_fsa_state_with_loop}

        assert (
            valid_fsa.transition_table.transition_count()
            == total_transitions - transition_remove_count
        )
        assert not any(
            state == valid_fsa_state_with_loop
            for state, _ in valid_fsa.transition_table.keys()
        )
        assert not any(
            valid_fsa_state_with_loop in next_states
            for next_states in valid_fsa.transition_table.values()
        )

    def test_discard_state_discards_transitions(
        self, valid_fsa: FSA, valid_fsa_state_with_loop: State
    ):
        transition_remove_count: int = valid_fsa.transition_table.transition_count(
            valid_fsa_state_with_loop
        )
        total_transitions: int = valid_fsa.transition_table.transition_count()

        valid_fsa.states.discard(valid_fsa_state_with_loop)

        assert (
            valid_fsa.transition_table.transition_count()
            == total_transitions - transition_remove_count
        )
        assert not any(
            state == valid_fsa_state_with_loop
            for state, _ in valid_fsa.transition_table.keys()
        )
        assert not any(
            valid_fsa_state_with_loop in next_states
            for next_states in valid_fsa.transition_table.values()
        )

    def test_discard_symbol_discards_transitions(
        self, valid_fsa: FSA, valid_fsa_symbol: Symbol
    ):
        states: Set[State] = valid_fsa.states
        total_transitions: int = valid_fsa.transition_table.transition_count()
        symbol_transitions: int = valid_fsa.transition_table.transition_count(
            valid_fsa_symbol
        )

        valid_fsa.alphabet.discard(valid_fsa_symbol)

        assert valid_fsa.states == states
        assert (
            valid_fsa.transition_table.transition_count()
            == total_transitions - symbol_transitions
        )
        assert not any(
            s == valid_fsa_symbol for _, s in valid_fsa.transition_table.keys()
        )

    def test_set_alphabet_discards_transitions(
        self, valid_fsa: FSA, valid_fsa_symbol: Symbol
    ):
        states: Set[State] = valid_fsa.states
        total_transitions: int = valid_fsa.transition_table.transition_count()
        symbol_transitions: int = valid_fsa.transition_table.transition_count(
            valid_fsa_symbol
        )
        new_alphabet: Alphabet = Alphabet(valid_fsa.alphabet - {valid_fsa_symbol})

        valid_fsa.alphabet = new_alphabet

        assert valid_fsa.states == states
        assert (
            valid_fsa.transition_table.transition_count()
            == total_transitions - symbol_transitions
        )
        assert not any(
            s == valid_fsa_symbol for _, s in valid_fsa.transition_table.keys()
        )

    def test_set_transitions(
        self, valid_fsa: FSA, valid_fsa_symbol: Symbol, valid_fsa_state: State
    ):
        valid_fsa.transition_table[(valid_fsa.initial_state, valid_fsa_symbol)] = {
            valid_fsa_state
        }

    def test_set_transitions_validates_start_state(
        self,
        valid_fsa: FSA,
        state_not_in_valid_fsa: State,
        valid_fsa_symbol: Symbol,
        valid_fsa_state: State,
    ):
        with pytest.raises(ValueError):
            valid_fsa.transition_table[(state_not_in_valid_fsa, valid_fsa_symbol)] = {
                valid_fsa_state
            }

    def test_set_transitions_validates_symbol_not_in_alphabet(
        self, valid_fsa: FSA, symbol_not_in_valid_fsa: Symbol, valid_fsa_state: State
    ):
        with pytest.raises(ValueError):
            valid_fsa.transition_table[
                (valid_fsa.initial_state, symbol_not_in_valid_fsa)
            ] = {valid_fsa_state}

    def test_set_transitions_rejects_non_epsilon_word(
        self, valid_fsa: FSA, non_epsilon_word: Word, valid_fsa_state: State
    ):
        with pytest.raises(ValueError):
            valid_fsa.transition_table[(valid_fsa.initial_state, non_epsilon_word)] = {
                valid_fsa_state
            }

    def test_set_transitions_validates_next_states(
        self,
        valid_fsa: FSA,
        valid_fsa_symbol: Symbol,
        valid_fsa_state: State,
        state_not_in_valid_fsa: State,
    ):
        with pytest.raises(ValueError):
            valid_fsa.transition_table[(valid_fsa_state, valid_fsa_symbol)] = (
                valid_fsa.states | {state_not_in_valid_fsa}
            )

    def test_add_transition_validates_next_state(
        self,
        valid_fsa: FSA,
        valid_fsa_state: State,
        valid_fsa_symbol: Symbol,
        state_not_in_valid_fsa: State,
    ):
        with pytest.raises(ValueError):
            valid_fsa.transition_table[(valid_fsa_state, valid_fsa_symbol)].add(
                state_not_in_valid_fsa
            )
