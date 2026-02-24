from __future__ import annotations
from collections import defaultdict, deque
from graphviz import Digraph
import pprint

class FSA:
    type Alphabet = set[str]
    type Transition = tuple[State, str, State]
    type TransitionTable = defaultdict[tuple[State, str], set[State]]

    _transitions: set[Transition]
    _alphabet: Alphabet
    _states: set[State]
    _initial_state: State
    _final_states: set[State]

    def __init__(
        self,
        transitions: set[Transition],
        alphabet: Alphabet,
        states: set[State],
        initial_state: State,
        final_states: set[State]
    ):
        # independent variables, no validation needed
        self._initial_state = initial_state
        self._alphabet = alphabet

        error_msg: str | None = self._validate_states(states)

        if error_msg is not None: raise ValueError(error_msg)

        self._states = states
        self.final_states = final_states
        self.transitions = transitions

    class State:
        label: str

        def __init__(self, label: str):
            self.label = label

    @property
    def states(self) -> set[State]:
        return self._states

    @states.setter
    def states(self, incoming_states: set[State]) -> None:
        """Set the states of the automaton.

        As a side effect, the method removes any final states not in the new set of states to preserve integrity.
        
        Raises:
            ValueError: If the set of new states does not contain the current initial state or if the given labels for the new states are not unique
        """
        error_msg: str | None = self._validate_states(incoming_states)

        if error_msg is not None: raise ValueError(error_msg)
        
        self.final_states -= incoming_states # remove any final states that will no longer exist
        self.transitions -= {
            (start_state, letter, end_state)
            for start_state, letter, end_state in self.transitions
            if start_state not in incoming_states
            or end_state not in incoming_states
        } # remove any transitions for states that will no longer exist
        self._states = incoming_states

    @property
    def initial_state(self) -> State:
        return self._initial_state

    @initial_state.setter
    def initial_state(self, new_initial: State) -> None:
        if new_initial not in self.states:
            raise ValueError("The initial state must be in the set of states")

        self._initial_state = new_initial

    @property
    def final_states(self) -> set[State]:
        return self._final_states

    @final_states.setter
    def final_states(self, incoming_final_states: set[State]) -> None:
        """Set the automaton's final states.

        Raises:
            ValueError: If any new final state is not in the current set of states.
        """
        if not incoming_final_states <= self.states:
            raise ValueError("All final states must be in the set of states")

        self._final_states = incoming_final_states
    
    @property
    def alphabet(self) -> Alphabet:
        return self._alphabet

    @alphabet.setter
    def alphabet(self, incoming_alphabet: Alphabet) -> None:
        """Set the alphabet of the automaton.

        As a side effect, the method removes transitions from the automaton where a transition's letter is not in the new alphabet to preserve integrity.
        """
        self.transitions -= {
            (start_state, letter, end_state)
            for start_state, letter, end_state in self.transitions
            if letter not in incoming_alphabet
        } # remove any transitions with letters that will no longer exist

        self._alphabet = incoming_alphabet

    @property
    def transitions(self) -> set[Transition]:
        return self._transitions

    @transitions.setter
    def transitions(self, incoming_transitions: set[Transition]) -> None:
        """Set the transitions of the automaton.

        Raises:
            ValueError: If there is at least 1 incoming transition such that its start or end states are not in the current set of states or its letter is not in the current alphabet.
        """
        if any(
            start_state not in self.states
            or end_state not in self.states
            or letter not in self.alphabet
            for start_state, letter, end_state in incoming_transitions
        ): raise ValueError("All transition states must be in the set of states and all transition letters must be in the alphabet")
    
        self._transitions = incoming_transitions
   
    @property
    def deterministic(self) -> bool:
        return all(len(end_states) <= 1 for end_states in self.transition_table.values()) 

    @property
    def transition_table(self) -> TransitionTable:
        al: TransitionTable = defaultdict(set) 

        for start_state, letter, end_state in self.transitions:
            al[(start_state, letter)].add(end_state)

        return al 

    @property
    def epsilon_closure(self) -> set[State]:
        transition_table: TransitionTable = self.transition_table
        closure: set[State] = {self.initial_state}
        queue: deque[State] = deque([self.initial_state])

        while queue:
            current: State = queue.popleft()
            next_states: set[State] = transition_table[(current, "")]

            for state in next_states:
                if state not in closure:
                    closure.add(state)
                    queue.append(state)

        return closure 

    def get_deterministic(self) -> FSA:
        if self.deterministic: return self

        transition_table: TransitionTable = self.transition_table
        epsilon_closure: set[State] = self.epsilon_closure

    def _validate_states(self, states: set[State]) -> str | None:
        """Validate whether the given set of states is a valid assignment for the automaton's states.

        Returns:
            None | str: None if validation passed or an error message if validation failed.
        
        Raises:
            ValueError: If the set of new states does not contain the current initial state or if the given labels for the new states are not unique
        """
        if self.initial_state not in states:
            return "The initial state must be in the set of states"

        if len([state.label for state in states]) != len({state.label for state in states}):
            return "All states must have unique labels"
        
        return None


    def draw(self, filename: str, open_file: bool = True) -> None:
        graph: Digraph = Digraph("FSA", format="png")

        graph.attr(rankdir="LR")

        for state in self.states:
            shape: str = "doublecircle" if state in self.final_states else "circle"

            graph.node(state.label, shape=shape)

        for start_state, letter, end_state in self.transitions:
            graph.edge(start_state.label, end_state.label, label=letter)

        graph.node("start", label="", shape="none", width="0", height="0")
        graph.edge("start", self.initial_state.label)

        graph.render(filename, view=open_file)




q: list[FSA.State] = [FSA.State("q0"), FSA.State("q1"), FSA.State("q2")]

fsa: FSA = FSA(
    states=set(q),
    initial_state=q[0],
    final_states={q[1]},
    alphabet={"a", "b"},
    transitions={
        (q[0], "a", q[0]),
        (q[0], "b", q[1]),
        (q[1], "a", q[1]),
        (q[1], "b", q[2]),
        (q[2], "a", q[2]),
        (q[2], "b", q[0]),
    }
)

fsa.draw("fsa_output")
