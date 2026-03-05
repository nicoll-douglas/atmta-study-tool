from collections import deque
from typing import TYPE_CHECKING
from .accepts import accepts

if TYPE_CHECKING:
    from ..state import State
    from ..fsa import FSA

def _recognizes_empty_language(fsa: FSA) -> bool:
    """Return True if the given FSA recognzies the empty language (a set 
    with no words), otherwise False.
    """ 
    visited: set[State] = {fsa.initial_state}
    queue: deque[State] = deque([fsa.initial_state])

    while queue:
        current_state: State = queue.popleft()
        
        if current_state in fsa.final_states:
            return False
        
        for (start_state, _), next_states in (
            fsa.transition_table.items()
        ):
            if start_state == current_state:
                for next_state in next_states:
                    if next_state not in visited:
                        visited.add(next_state)
                        queue.append(next_state)
                        
    return True

def recognizes(fsa: FSA, language: set[str]) -> bool:
    """Return True if the given FSA recognizes the given language, 
    otherwise False."""
    if not language: return _recognizes_empty_language()

    return all(accepts(fsa, word) for word in language)