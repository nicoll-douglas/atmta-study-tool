from __future__ import annotations
from collections import defaultdict, deque
from collections.abc import Set
from graphviz import Digraph

class FSA:
    """Represents a finite-state automaton (FSA) and contains algorithms that operate on it."""

    EPSILON: str = ""

    type Alphabet = set[str]
    type Transition = tuple[State, str, State]
    type TransitionTable = defaultdict[tuple[State, str], set[State]]
    type DFASetTransitionTable = dict[tuple[frozenset[State], str], frozenset[State]]

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
        # assign initial state without validation
        self._initial_state = initial_state

        # validate and assign alphabet and states without side effects on attributes that don't yet exist
        self._validate_alphabet(alphabet)
        self._alphabet = alphabet
        self._validate_states(states)
        self._states = states

        # validate and assign final states and transitions
        self.final_states = final_states
        self.transitions = transitions

    class State:
        """Represents a state in the FSA."""

        label: str # the state's arbitrary label for diagrams

        def __init__(self, label: str | Set[FSA.State]):
            if isinstance(label, str):
                self.label = label
            else:
                self.label = "{" + ", ".join(state.label for state in label) + "}"

    @property
    def states(self) -> set[State]:
        """Get the FSA's set of states."""
        return self._states

    @states.setter
    def states(self, incoming_states: set[State]) -> None:
        """Set the states of the FSA.

        As a side effect, the method removes any final states and transitions containing states not in the new set of states to preserve integrity.
        
        Raises:
            ValueError: If the new set of states does not contain the current initial state or if the given labels for the new states are not unique.
        """
        self._validate_states(incoming_states)
        
        self.final_states -= incoming_states # remove any final states that will no longer exist
        self.transitions -= {
            (start_state, label, end_state)
            for start_state, label, end_state in self.transitions
            if start_state not in incoming_states
            or end_state not in incoming_states
        } # remove any transitions for states that will no longer exist
        self._states = incoming_states

    @property
    def initial_state(self) -> State:
        """Get the initial state of the FSA."""
        return self._initial_state

    @initial_state.setter
    def initial_state(self, new_initial: State) -> None:
        """Set the initial state of the FSA.

        Args:
            new_initial: A state in the current set of states.

        Raises:
            ValueError: If the new initial state is not in the current of states.
        """
        if new_initial not in self.states:
            raise ValueError("The initial state must be in the set of states")

        self._initial_state = new_initial

    @property
    def final_states(self) -> set[State]:
        """Get the final states of the FSA."""
        return self._final_states

    @final_states.setter
    def final_states(self, incoming_final_states: set[State]) -> None:
        """Set the final states of the FSA. 

        Args:
            incoming_final_states: A subset of the current set of states.

        Raises:
            ValueError: If any new final state is not in the current set of states.
        """
        if not incoming_final_states <= self.states:
            raise ValueError("All final states must be in the set of states")

        self._final_states = incoming_final_states
    
    @property
    def alphabet(self) -> Alphabet:
        """Get the alphabet of the FSA."""
        return self._alphabet

    @alphabet.setter
    def alphabet(self, incoming_alphabet: Alphabet) -> None:
        """Set the alphabet of the FSA.

        As a side effect, the method removes transitions from the FSA where a transition's label is not in the new alphabet and not equal to epsilon to preserve integrity.

        Args:
            incoming_alphabet: Must be a set of strings such that all strings are of length 1.

        Raises:
            ValueError: If there is any letter in given alphabet that isn't of length 1.
        """
        self._validate_alphabet(incoming_alphabet)

        self.transitions -= {
            (start_state, label, end_state)
            for start_state, label, end_state in self.transitions
            if label not in incoming_alphabet
            and label != self.__class__.EPSILON
        } # remove any transitions with letters that will no longer exist

        self._alphabet = incoming_alphabet

    @property
    def transitions(self) -> set[Transition]:
        """Get the transitions of the FSA."""
        return self._transitions

    @transitions.setter
    def transitions(self, incoming_transitions: set[Transition]) -> None:
        """Set the transitions of the FSA.

        Args:
            incoming_transitions: A new set of transitions constructed from states in the current set of states and letters in the current alphabet or epsilon.

        Raises:
            ValueError: If there is at least 1 incoming transition such that its start or end states are not in the current set of states, or, its label is not in the current alphabet or not equal to epsilon.
        """
        if any(
            start_state not in self.states
            or end_state not in self.states
            or (label not in self.alphabet and label != self.__class__.EPSILON)
            for start_state, label, end_state in incoming_transitions
        ): raise ValueError("All transition states must be in the set of states, and all transition labels must be a letter in the alphabet or epsilon")
    
        self._transitions = incoming_transitions
   
    @property
    def is_dfa(self) -> bool:
        """Return a boolean flag indicating whether the FSA is a deterministic FSA (DFA) or not."""
        return all(
            label != self.__class__.EPSILON
            and len(end_states) <= 1
            for (_, label), end_states in self.transition_table.items()
        )
    
    @property
    def is_complete_dfa(self) -> bool:
        """Return a boolean flag indicating whether the FSA is a complete DFA.

        A complete DFA must have exactly 1 outgoing transition for every combination of state and letter.
        """
        transition_table: FSA.TransitionTable = self.transition_table
        
        return self.is_dfa and all(
            len(transition_table[(state, letter)]) == 1
            for letter in self.alphabet
            for state in self.states
        )

    @property
    def is_nfa(self) -> bool:
        """Return a boolean flag indicating whether the FSA is a non-deterministic FSA (NFA) or not."""
        return not self.is_dfa

    @property
    def is_epsilon_nfa(self) -> bool:
        """Return a boolean flag indicating whether the FSA is an epsilon-NFA or not."""
        return self.is_nfa and any(
            label == self.__class__.EPSILON
            for _, label, _ in self.transitions
        )

    @property
    def type(self) -> str:
        """Get a string description of the type of the FSA."""
        if self.is_complete_dfa: return "Complete DFA"
        if self.is_dfa: return "DFA"
        if self.is_epsilon_nfa: return "Epsilon-NFA"

        return "NFA"

    @property
    def transition_table(self) -> TransitionTable:
        """Get the transition table of the FSA.

        The transition table consists of a dictionary mapping column and row pairs (start states and labels which form a transition) to an entry in the table (the set of possible states that can be reached after the transition).
        """
        transition_table: FSA.TransitionTable = defaultdict(set) 

        for start_state, label, end_state in self.transitions:
            transition_table[(start_state, label)].add(end_state)

        return transition_table

    def epsilon_closure(self, starting_state: State) -> set[State]:
        """Get the epsilon-closure of a state in the FSA.

        Args:
            starting_state: The starting state from which to start considering epsilon transitions.

        Returns:
            set[State]: The epsilon-closure containing all states that can be reached by only following epsilon-transitions from the given state. At minimum this will be a set of length 1 including the given state.
        """
        if starting_state not in self.states: raise ValueError("Starting state must be in the set of states to find the epsilon-closure")

        transition_table: FSA.TransitionTable = self.transition_table
        closure: set[FSA.State] = {starting_state}
        queue: deque[FSA.State] = deque([starting_state])

        while queue:
            current: FSA.State = queue.popleft()
            next_states: set[FSA.State] = transition_table[(current, self.__class__.EPSILON)]

            for state in next_states:
                if state not in closure:
                    closure.add(state)
                    queue.append(state)

        return closure 

    def subset_construction(self) -> FSA:
        """Construct an equivalent deterministic FSA from the current FSA via the subset construction algorithm.

        The method does not guarantee that the resulting FSA will be a complete DFA, only a DFA.

        Returns:
            FSA: An equivalent deterministic FSA or a reference to the FSA itself if already deterministic.
        """
        if self.is_dfa: return self

        # step 1: get the NFA transition table and DFA initial state (NFA epsilon closure)
        nfa_transition_table: FSA.TransitionTable = self.transition_table
        dfa_initial_state: frozenset[FSA.State] = frozenset(self.epsilon_closure(self.initial_state))

        # step 2: discover all DFA states and construct the DFA transition table 
        queue: deque[frozenset[FSA.State]] = deque([dfa_initial_state])
        dfa_states: set[frozenset[FSA.State]] = {dfa_initial_state}
        dfa_transition_table: FSA.DFASetTransitionTable = {}

        while queue:
            current_dfa_state: frozenset[FSA.State] = queue.popleft()

            for letter in self.alphabet:
                # step 2.1: find all reachable states in the NFA from the set of NFA states in the current DFA states
                reachable_states: set[FSA.State] = set()

                for nfa_state in current_dfa_state:
                    for transition_state in nfa_transition_table[(nfa_state, letter)]:
                        reachable_states.update(self.epsilon_closure(transition_state))

                # step 2.2: construct the next DFA state from the reachables
                next_dfa_state: frozenset[FSA.State] = frozenset(reachable_states)

                # if nothing is reachable, then we will point the transition to the dummy state (represented by the empty set here)
                dfa_transition_table[(current_dfa_state, letter)] = next_dfa_state

                if next_dfa_state not in dfa_states:
                    dfa_states.add(next_dfa_state) 
                    queue.append(next_dfa_state)
        
        # step 3: construct the new automaton and identify the DFA final states
        dfa_state_map: dict[frozenset[FSA.State], FSA.State] = {
            dfa_state: self.State(dfa_state)
            for dfa_state in dfa_states
        }

        return FSA(
            alphabet=self.alphabet,
            initial_state=dfa_state_map[dfa_initial_state],
            final_states={
                dfa_state_map[dfa_state]
                for dfa_state in dfa_states
                if any(nfa_state in self.final_states for nfa_state in dfa_state)
            },
            states=set(dfa_state_map.values()),
            transitions={
                (dfa_state_map[start_state], label, dfa_state_map[end_state])
                for (start_state, label), end_state in dfa_transition_table.items()
            }
        )
       
    def _validate_states(self, states: set[State]) -> None:
        """Validate whether the given set of states is a valid assignment for the FSA's states.

        Raises:
            ValueError: If the current initial state is not in the given set of states or the states don't have unique labels.
        """
        if self.initial_state not in states:
            raise ValueError("The initial state must be in the set of states")

        if len([state.label for state in states]) != len({state.label for state in states}):
            raise ValueError("All states must have unique labels")

        return None

    def _validate_alphabet(self, alphabet: Alphabet) -> None:
        """Validate whether the given alphabet is a valid assignment for the FSA's alphabet.

        Raises:
            ValueError: If the alphabet contains 1 or more strings that are not of length 1.
        """
        if any(len(letter) != 1 for letter in alphabet):
            raise ValueError("All letters in the alphabet must be a string of length 1")

    def draw(self, filename: str, open_file: bool = True) -> None:
        """Create an image representation of the FSA and optionally open the image file.

        Args:
            filename: The extension-less filename to give the .png file.
            open_file: Whether to open the .png file for immediate viewing.
        """
        graph: Digraph = Digraph("FSA", format="png")

        graph.attr(rankdir="LR")

        for state in self.states:
            shape: str = "doublecircle" if state in self.final_states else "circle"

            graph.node(state.label, shape=shape)

        for start_state, label, end_state in self.transitions:
            graph.edge(start_state.label, end_state.label, label=label)

        graph.node("start", label="", shape="none", width="0", height="0")
        graph.edge("start", self.initial_state.label)
        graph.render(filename, view=open_file, cleanup=True)

def example_1() -> None:
    q: list[FSA.State] = [FSA.State(f"q{i}") for i in range(4)] # list of the FSA's states for quick positional access
    fsa: FSA = FSA(
        states=set(q),
        initial_state=q[0],
        final_states={q[3]},
        alphabet={"0", "1", "2"},
        transitions={
            (q[0], "0", q[1]),
            (q[1], "1", q[1]),
            (q[1], "1", q[2]),
            (q[1], "1", q[3]),
            (q[2], "1", q[3]),
            (q[2], "2", q[2]),
            (q[3], "0", q[2])
        }
    )

    print("Example 1:", fsa.type)
    fsa.draw("example_1")

    dfa_equivalent: FSA = fsa.subset_construction()

    print("Example 1 Equivalent DFA:", dfa_equivalent.type)
    dfa_equivalent.draw("example_1_dfa_equivalent")

example_1()
