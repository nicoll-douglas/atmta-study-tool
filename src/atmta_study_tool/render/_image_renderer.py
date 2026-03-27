from pathlib import Path


class ImageRenderer:
    """Represents an image renderer that outputs images to disk."""

    # the default directory where renders should go relative to the cwd of the program
    _BASE_RENDER_DIR: Path = Path("renders")
    # the output directory where rendered images should go
    _render_dir: Path

    def __init__(self, render_dir: Path | str) -> None:
        self._render_dir = ImageRenderer._BASE_RENDER_DIR / render_dir
