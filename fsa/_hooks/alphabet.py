from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ..models.transition_table import TransitionTable
    from models.symbol import Symbol
    from models.alphabet import Alphabet


def post_discard(symbol: Symbol, transition_table: TransitionTable) -> None:
    """Remove transitions from the given transition table if they utilise the given symbol.

    This hook is intended to run after the symbol is discarded from an FSA's alphabet.

    Args:
        symbol: The symbol discarded from the FSA's alphabet.
        transition_table: The transition table of the FSA.
    """
    transition_table.remove_such_that(lambda key, _: symbol == key[1])


def post_set(alphabet: Alphabet, transition_table: TransitionTable) -> None:
    """Remove transitions from the given transition table that utilise any symbol not in the given alphabet.

    This hook is intended to run after the alphabet is set for an FSA.

    Args:
        alphabet: An alphabet set for an FSA.
        transition_table: The transition table of the FSA.
    """
    transition_table.remove_such_that(lambda key, _: key[1] not in alphabet)
