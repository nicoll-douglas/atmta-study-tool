from typing import AbstractSet
from utils import sorted_comma_sep_string

class State:
    """Represents a state in an FSA."""

    # the state's arbitrary label for diagrams
    _label: str 

    def __init__(self, label: str | AbstractSet[State]):
        self._label = (
            label 
            if isinstance(label, str)
            else (
                "{" + sorted_comma_sep_string(
                    state.label for state in label
                ) + "}"
            )
        )

    @property
    def label(self) -> str:
        return self._label
    
    @staticmethod
    def label_is_unique(state: State, states: AbstractSet[State]) -> bool:
        """Return True if the label of the given state is unique 
        amongst the given states.
        
        The set of states is assumed to already have unique labels.
        """
        return state in states or state.label not in {s.label for s in states}

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.label}')"