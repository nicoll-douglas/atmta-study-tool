from ..models.state import State


def states(n: int, label_prefix: str = "q") -> list[State]:
    """Return n states numbered 0 to n-1 with the given label prefix."""
    return [State(f"{label_prefix}{i}") for i in range(n)]
