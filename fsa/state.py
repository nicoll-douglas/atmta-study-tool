from __future__ import annotations
from typing import Iterable, Any

class State:
    """Represents a state in an FSA."""

    # the state's arbitrary label for diagrams
    _label: str 

    def __init__(self, label: str | Iterable[Any]):
        if isinstance(label, str):
            self._label = label
        else:
            self._label = (
                "{" + ", ".join(
                    str(item) for item in label
                ) + "}"
            )

    @property
    def label(self) -> str:
        return self._label
    
    @staticmethod
    def label_is_unique(state: State, states: Iterable[State]) -> bool:
        """Return True if the label of the given state is unique 
        amongst the given states.
        
        The given iterable of states is assumed to already have unique labels.
        """
        return state in states or state.label not in {s.label for s in states}
    
    def __str__(self) -> str:
        return self.label

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.label}')"