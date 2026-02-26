from typing import Set

class State:
    """Represents a state in an FSA."""

    # the state's arbitrary label for diagrams
    _label: str 

    def __init__(self, label: str | Set[State]):
        self.label = label

    @property
    def label(self) -> str:
        return self._label

    @label.setter
    def label(self, value: str | Set[State]) -> None:
        self._label = (
            value 
            if isinstance(value, str)
            else (
                "{" + ", ".join(state.label for state in value) + "}"
            )
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.label}')"