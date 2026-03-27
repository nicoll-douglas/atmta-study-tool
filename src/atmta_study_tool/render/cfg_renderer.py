from atmta_study_tool.cfg import CFG
from ._text_renderer import TextRenderer


class CFGRenderer(TextRenderer):
    """Represents a renderer object that can render CFGs as text."""

    def print_rules(self, cfg: CFG) -> None:
        """Print the given CFG as a list of its rules."""
        print("Starting variable:", cfg.starting_variable)

        for rule in cfg.rules:
            print(rule)

    def print_formal(self, cfg: CFG) -> None:
        """Print the given CFG as its formal 4-tuple definition."""
        four_tuple: str = self._get_tuple_str(
            [
                self._get_set_str(cfg.alphabet),
                self._get_set_str(cfg.variables),
                self._get_set_str(cfg.rules),
                cfg.starting_variable,
            ]
        )

        print(four_tuple)
