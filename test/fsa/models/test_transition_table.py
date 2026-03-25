from fsa.models.transition_table import TransitionTable
from test.types import TransitionCountData
from functools import reduce


class TestTransitionTable:
    def test_incoming_transition_count(
        self,
        transition_table: TransitionTable,
        transition_table_counts: TransitionCountData,
    ):
        for state, count_data in transition_table_counts[0].items():
            assert (
                transition_table.incoming_transition_count(state)
                == count_data["incoming"]
            )

    def test_outgoing_transition_count(
        self,
        transition_table: TransitionTable,
        transition_table_counts: TransitionCountData,
    ):
        for state, count_data in transition_table_counts[0].items():
            assert (
                transition_table.outgoing_transition_count(state)
                == count_data["outgoing"]
            )

    def test_loop_transition_count(
        self,
        transition_table: TransitionTable,
        transition_table_counts: TransitionCountData,
    ):
        for state, count_data in transition_table_counts[0].items():
            assert transition_table.loop_transition_count(state) == count_data["loop"]

    def test_state_transition_count(
        self,
        transition_table: TransitionTable,
        transition_table_counts: TransitionCountData,
    ):
        for state, count_data in transition_table_counts[0].items():
            assert transition_table.transition_count(state) == sum(count_data.values())

    def test_symbol_transition_count(
        self,
        transition_table: TransitionTable,
        transition_table_counts: TransitionCountData,
    ):
        for symbol, count in transition_table_counts[1].items():
            assert transition_table.transition_count(symbol) == count

    def test_transition_count(
        self,
        transition_table: TransitionTable,
        transition_table_counts: TransitionCountData,
    ):
        assert transition_table.transition_count() == sum(
            transition_table_counts[1].values()
        )
