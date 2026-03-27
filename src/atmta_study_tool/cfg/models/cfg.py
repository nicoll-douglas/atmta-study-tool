from .variable import Variable
from .rule import Rule
from atmta_study_tool.language import Alphabet, Symbol
from atmta_study_tool._common.data_structures import (
    ObservableSet,
    ObservableSetController,
)
from collections.abc import Set


class CFG:
    """Represents a context-free grammar (CFG)."""

    # the starting variable of the grammar
    _starting_variable: Variable
    # the alphabet of the grammar
    _alphabet: Alphabet
    # the variables of the grammar
    _variables: ObservableSet[Variable]
    # the rules of the grammar
    _rules: ObservableSet[Rule]

    def __init__(
        self,
        alphabet: Alphabet,
        variables: Set[Variable],
        rules: Set[Rule],
        starting_variable: Variable,
    ):
        self.starting_variable = starting_variable
        self.variables = variables
        self.alphabet = alphabet
        self.rules = rules

    @property
    def starting_variable(self) -> Variable:
        return self._starting_variable

    @starting_variable.setter
    def starting_variable(self, new_value: Variable) -> None:
        if hasattr(self, "_variables") and new_value not in self.variables:
            raise ValueError(
                f"Expected a variable in the set of variables {self.variables!r}. Got {new_value!r}."
            )

        self._starting_variable = new_value

    @property
    def variables(self) -> ObservableSet[Variable]:
        return self._variables

    @variables.setter
    def variables(self, new_value: Set[Variable]) -> None:
        if self.starting_variable not in new_value:
            raise ValueError(
                f"Expected a set of variables with the starting variable {self.starting_variable!r}. Got {new_value!r}."
            )

        def _pre_discard(variable: Variable) -> None:
            if variable == self.starting_variable:
                raise ValueError(
                    f"Expected a variable not equal to the starting variable {self.starting_variable!r}. Got {variable!r}."
                )

        self._variables = ObservableSet[Variable](
            new_value,
            pre_discard=_pre_discard,
            post_discard=lambda v: self._discard_rules_that_contain(v),
        )

        if hasattr(self, "_rules"):
            for rule in list(self.rules):
                # discard rules that contain variables not in the new set of variables
                if rule.LHS not in self.variables or (
                    set(filter(lambda symbol: isinstance(symbol, Variable), rule.RHS))
                    - self.variables
                ):
                    self.rules.discard(rule)

    @property
    def rules(self) -> ObservableSet[Rule]:
        return self._rules

    @rules.setter
    def rules(self, new_value: Set[Rule]) -> None:
        def _pre_add(rule: Rule):
            if rule.LHS not in self.variables:
                raise ValueError(
                    f"Expected a variable in the set of variables {self.variables!r}. Got {rule.LHS!r}."
                )

            if set(rule.RHS) - (self.variables | self.alphabet):
                raise ValueError(
                    f"Expected a word containing variables in the set of variables {self.variables!r} and symbols in the alphabet {self.alphabet!r}. Got {rule.RHS!r}."
                )

        self._rules = ObservableSet[Rule](new_value, pre_add=_pre_add)

    @property
    def alphabet(self) -> Alphabet:
        return self._alphabet

    @alphabet.setter
    def alphabet(self, new_value: Alphabet) -> None:
        ObservableSetController.set__post_discard(
            new_value, lambda s: self._discard_rules_that_contain(s)
        )

        self._alphabet = new_value

        if hasattr(self, "_rules"):
            for rule in list(self.rules):
                # check for terminal symbols in the RHS left over that are not in the new alphabet
                if (
                    set(
                        filter(
                            lambda symbol: not isinstance(symbol, Variable), rule.RHS
                        )
                    )
                    - self.alphabet
                ):
                    self.rules.discard(rule)

    # TODO: remove str method
    def __str__(self) -> str:
        return "\n".join(str(rule) for rule in self.rules)

    def _discard_rules_that_contain(self, symbol: Symbol) -> None:
        """Discard rules from the CFG ruleset that the given symbol."""
        for rule in list(filter(lambda rule: symbol in rule, self.rules)):
            self.rules.discard(rule)
