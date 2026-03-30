from atmta_study_tool.language import Symbol, Word
from .abstract_fsa import AbstractFSA
from .state import State
from collections import deque
from collections.abc import Set
from .transition_table import TransitionTable
from .marking_table import MarkingTable
from atmta_study_tool._common.data_structures import DisjointSetUnion


class FSA[U: (str, frozenset[State]) = str](AbstractFSA[U]):
    """Represents a concrete Finite-State Automaton (FSA)."""

    def _validate_symbol(self, symbol: Symbol) -> None:
        """Validate that the given symbol is the alphabet if not epsilon."""
        if symbol == Symbol.EPSILON:
            return

        super()._validate_symbol(symbol)

    def epsilon_closure(self, states: Set[State]) -> set[State]:
        """Get the epsilon-closure of a set of states in the FSA.

        Args:
            states: The set of starting states from which to start considering epsilon transitions.

        Returns:
            The epsilon-closure which contains all states that can be reached by only following epsilon-transitions from the given states. At minimum this will be a set states including all the given states.
        """
        closure: set[State] = set(states)
        queue: deque[State] = deque(closure)

        while queue:
            current_state: State = queue.popleft()
            next_states: set[State] = self.delta(current_state, Symbol.EPSILON)

            for state in next_states:
                if state not in closure:
                    closure.add(state)
                    queue.append(state)

        return closure

    def epsilon_remove(self) -> None:
        """Remove all epsilon transitions from the FSA."""
        new_transition_table: TransitionTable[U] = TransitionTable()
        new_final_states: set[State] = set()
        e_closures: dict[State[U], set[State[U]]] = {
            state: self.epsilon_closure({state}) for state in self.states
        }

        for state in self.states:
            e_closure: set[State[U]] = e_closures[state]

            for symbol in self.alphabet:
                # delta'(q, a) = E(delta(E(q), a))
                new_transition_table[(state, symbol)] = self.epsilon_closure(
                    self.delta(e_closures[state], symbol)
                )

            # S & E(q) != {}
            if self.final_states & e_closure:
                new_final_states.add(state)

        self.final_states = new_final_states
        self.transition_table = new_transition_table

    def is_complete(self) -> bool:
        """Return True if the FSA is complete or False otherwise."""
        return all(
            len(self.delta(state, symbol)) != 0
            for state in self.states
            for symbol in self.alphabet
        )

    def is_deterministic(self) -> bool:
        """Return True if the FSA is deterministic (a DFA) or False otherwise."""
        return all(
            len(self.delta(state, symbol)) > 1
            for state in self.states
            for symbol in self.alphabet
        )

    def has_epsilon(self) -> bool:
        """Return True if the FSA has any epsilon transitions (an epsilon-NFA) or False otherwise."""
        return any(
            symbol == Symbol.EPSILON and next_states
            for (_, symbol), next_states in self.transition_table.items()
        )

    def complete(self, dead_state: State[U]) -> bool:
        """Complete the FSA adding the given dead state if necessary.

        Return:
            bool: True if the dead state was added or False otherwise.
        """
        found_missing: bool = False

        for state in list(self.states):
            for symbol in self.alphabet:
                if not self.delta(state, symbol):
                    if not found_missing:
                        self.states.add(dead_state)
                        found_missing = True

                    self.transition_table[(state, symbol)] = {dead_state}

        if found_missing:
            for symbol in self.alphabet:
                self.transition_table[(dead_state, symbol)] = {dead_state}

        return found_missing

    def subset_construction(self, complete: bool = False) -> FSA[frozenset[State]]:
        initial_state: State[frozenset[State]] = State(
            frozenset(self.epsilon_closure({self.initial_state}))
        )
        dfa: FSA[frozenset[State]] = FSA(
            initial_state=initial_state,
            states={initial_state},
            alphabet=self.alphabet.copy(),
        )
        states_unprocessed: deque[State[frozenset[State]]] = deque([initial_state])

        while states_unprocessed:
            current_dfa_state: State[frozenset[State]] = states_unprocessed.popleft()

            if current_dfa_state.UID & self.final_states:
                dfa.final_states.add(current_dfa_state)

            for symbol in dfa.alphabet:
                discovered_state: State[frozenset[State]] = State(
                    frozenset(
                        state
                        for nfa_state in current_dfa_state.UID
                        for state in self.epsilon_closure(self.delta(nfa_state, symbol))
                    )
                )

                if not discovered_state.UID and not complete:
                    continue

                if discovered_state not in dfa.states:
                    dfa.states.add(discovered_state)
                    states_unprocessed.append(discovered_state)

                dfa.transition_table[(current_dfa_state, symbol)] = {discovered_state}

        return dfa

    def complement(self) -> FSA[frozenset[State]]:
        """Create and return the complement automaton of the FSA."""
        dfa: FSA[frozenset[State]] = self.subset_construction(complete=True)
        non_final_states: Set[State[frozenset[State]]] = dfa.states - dfa.final_states

        dfa.final_states = non_final_states

        return dfa

    def accepts(self, word: Word) -> bool:
        """Return True if the FSA accepts the given word otherwise False."""
        dfa: FSA[frozenset[State]] = self.subset_construction()

        current_state: State = dfa.initial_state

        for symbol in word:
            next_states: set[State] = dfa.delta(current_state, symbol)

            if not next_states:
                # no next state so we hit a dead-end which means the word is not accepted
                return False

            # since we are traversing a DFA the set only has one state
            current_state = next_states.pop()

        # the word is accepted if after finishing traversal, the current state is a final state
        return current_state in dfa.final_states

    def minimized(self) -> FSA:
        """Perform the FSA minimization algorithm on the given FSA to create and return a new, minimized FSA."""

        dfa: FSA[frozenset[State]] = self.subset_construction(complete=True)

        marking_table: MarkingTable = MarkingTable(dfa.states)

        for row_state, col_state in marking_table.keys():
            if (row_state in dfa.final_states) ^ (col_state in dfa.final_states):
                marking_table.mark((row_state, col_state))

        mark_made: bool = True

        while mark_made:
            mark_made = False

            for key, marked in marking_table.items():
                if not marked:
                    for symbol in dfa.alphabet:
                        row_state, col_state = key

                        next_row_state: State[frozenset[State]] = dfa.delta(
                            row_state, symbol
                        ).pop()

                        next_col_state: State[frozenset[State]] = dfa.delta(
                            col_state, symbol
                        ).pop()

                        if next_row_state != next_col_state and marking_table.marked(
                            (next_row_state, next_col_state)
                        ):
                            marking_table.mark(key)
                            mark_made = True
                            break

        table_unions: DisjointSetUnion[State[frozenset[State]]] = DisjointSetUnion(
            marking_table.STATES
        )

        for (state_a, state_b), mark in marking_table.items():
            if not mark:
                table_unions.union(state_a, state_b)

        min_dfa_states: dict[State[frozenset[State]], tuple[set[State], State[str]]] = {
            representative: (states, State(f"q{index}"))
            for index, (representative, states) in enumerate(
                table_unions.sets().items()
            )
        }

        min_dfa: FSA = FSA(
            initial_state=min_dfa_states[table_unions.find(dfa.initial_state)][1],
            states=set(value[1] for value in min_dfa_states.values()),
            alphabet=dfa.alphabet.copy(),
        )

        for representative, (states, state) in min_dfa_states.items():
            for symbol in dfa.alphabet:
                next_dfa_state: State[frozenset[State]] = dfa.delta(
                    representative, symbol
                ).pop()

                next_dfa_state_repr: State[frozenset[State]] = table_unions.find(
                    next_dfa_state
                )

                min_dfa.transition_table[(state, symbol)] = {
                    min_dfa_states[next_dfa_state_repr][1]
                }

            if states & dfa.final_states:
                min_dfa.final_states.add(state)

        min_dfa.remove_unreachable_states()
        min_dfa.remove_unproductive_states()

        return min_dfa
