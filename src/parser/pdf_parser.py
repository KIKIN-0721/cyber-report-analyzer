from pathlib import Path
from typing import Dict, List


def extract_text_and_images(pdf_path: Path) -> Dict[str, List[str]]:
    """Return extracted text blocks and image paths.

    This is a skeleton API for S2 implementation.
    """
    if not isinstance(pdf_path, Path):
        raise TypeError("pdf_path must be a pathlib.Path")

    return {"text_blocks": [], "image_paths": []}
