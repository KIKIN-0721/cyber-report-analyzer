from pathlib import Path
from typing import Dict


def run_ocr(image_path: Path) -> Dict[str, str]:
    """Run OCR on one image and return normalized fields.

    This is a skeleton API for S2 implementation.
    """
    if not isinstance(image_path, Path):
        raise TypeError("image_path must be a pathlib.Path")

    return {"raw_text": "", "normalized_text": ""}
