import re
from pathlib import Path
from typing import Dict, List, Tuple

_CORRECTIONS: List[Dict[str, str]] = []


def _load_corrections() -> List[Dict[str, str]]:
    global _CORRECTIONS
    if _CORRECTIONS:
        return _CORRECTIONS
    dict_path = Path(__file__).with_name("correction_dict.yaml")
    if dict_path.exists():
        import yaml

        with open(dict_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            _CORRECTIONS = data.get("corrections", []) if data else []
    return _CORRECTIONS


def apply_correction(text: str) -> Tuple[str, str]:
    """Apply dictionary-based corrections to OCR text.

    Returns:
        (corrected_text, correction_type)
    """
    corrections = _load_corrections()
    corrected = text
    correction_type = "none"
    for item in corrections:
        error = item.get("error", "")
        correct = item.get("correct", "")
        if not error:
            continue
        pattern = re.escape(error)
        if re.search(pattern, corrected):
            corrected = re.sub(pattern, correct, corrected)
            correction_type = "dict"
    return corrected, correction_type
