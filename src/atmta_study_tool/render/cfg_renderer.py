from atmta_study_tool.cfg import CFG
from atmta_study_tool._common.utils import strings_from, str_set, str_tuple
from .printer import Printer


class CFGRenderer(Printer):
    """Represents a renderer object that can render CFGs as text."""

    def rules(self, cfg: CFG) -> str:
        """Print the given CFG as a list of its rules."""
        return f"Starting variable: {cfg.starting_variable}\n" + "\n".join(
            strings_from(cfg.rules)
        )

    def formal(self, cfg: CFG) -> str:
        """Print the given CFG as its formal 4-tuple definition."""
        four_tuple: str = str_tuple(
            (
                str_set(cfg.alphabet),
                str_set(cfg.variables),
                str_set(cfg.rules),
                str(cfg.starting_variable),
            )
        )

        return four_tuple
