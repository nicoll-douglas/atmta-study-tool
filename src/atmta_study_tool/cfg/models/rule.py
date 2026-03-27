from __future__ import annotations
from .variable import Variable
from atmta_study_tool.language import Word
from atmta_study_tool._common.constants import EPSILON_UID


class Rule:
    """Represents a rule in a CFA."""

    # the left-hand side of the rule
    _lhs: Variable
    # the right-hand side of the rule
    _rhs: Word

    def __init__(self, lhs: Variable, rhs: Word):
        self._lhs = lhs
        self._rhs = rhs

    @property
    def LHS(self) -> Variable:
        return self._lhs

    @property
    def RHS(self) -> Word:
        return self._rhs

    def __str__(self):
        return str(self.LHS) + " \u2192 " + str(self.RHS)

    def __repr__(self):
        return f"{self.__class__.__name__}(LHS={self.LHS!r}, RHS={self.RHS!r})"

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, Rule) and self.LHS == other.LHS and self.RHS == other.RHS
        )

    def __hash__(self):
        return hash((self.__class__, self.LHS, self.RHS))

    def __contains__(self, item: object):
        if item == Word.EPSILON:
            return item == self.RHS

        return self.LHS == item or item in self.RHS
