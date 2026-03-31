from pathlib import Path
from abc import abstractmethod
from os import PathLike
from typing import Literal
from ._renderer import Renderer


class ImageRenderer(Renderer):
    """Represents an image renderer that outputs images to disk."""

    # the output directory where rendered images should go
    _IMAGE_RENDER_DIR: Path = Renderer._RENDER_DIR / "img"

    type ImageFormat = Literal["png", "jpg", "jpeg", "svg", "webp"]

    @abstractmethod
    def image(self, filename: PathLike | str, format: ImageFormat) -> None:
        """Render an image with the given filename and format."""
        pass
