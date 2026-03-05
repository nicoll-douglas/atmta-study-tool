from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..state import State
    from lib import UnionFinder

def get_state_union_groupings(
    union_finder: UnionFinder[State]
) -> dict[State, set[State]]:
    groupings: dict[State, set[State]] = {}

    for state in union_finder.items():
        root: State = union_finder.find(state)

        if root not in groupings:
            groupings[root] = set()

        groupings[root].add(state)
    
    return groupings