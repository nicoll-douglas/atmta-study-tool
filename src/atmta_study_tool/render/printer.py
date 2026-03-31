from collections.abc import Iterable, Set
from os import PathLike
from ._renderer import Renderer
from pathlib import Path


class Printer(Renderer):
    """Represents a printer that prints content to stdout or a file."""

    # output directory where file-based prints should go
    _PRINT_FILE_DIR: Path = Renderer._RENDER_DIR / "txt"

    def print(self, content: str, filename: PathLike | str | None = None):
        """Print the given string content to the given file or stdout if None given."""
        if filename is None:
            print(content)
        else:
            path: Path = self._PRINT_FILE_DIR / Path(filename).with_suffix(".txt")

            with open(path, mode="w") as f:
                print(content, file=f)
