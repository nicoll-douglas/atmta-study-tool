from typing import Iterable

def sorted_comma_sep_string(iterable: Iterable) -> str:
    """Return a sorted, comma-separated string from the items in 
    the given iterable."""
    return ", ".join(sorted(iterable))