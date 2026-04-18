import re
from typing import Any, Dict, List, Tuple

from .correction import apply_correction
from .patterns import RSA_PATTERNS, TLS_PATTERNS, WEAK_ALGO_PATTERNS


def clean_text(ocr_lines: List[Any]) -> str:
    """Sort OCR lines by position and merge into a single clean text."""
    if not ocr_lines:
        return ""

    items = []
    for line in ocr_lines:
        if not line:
            continue
        bbox = line[0]
        text, _conf = line[1]
        ys = [p[1] for p in bbox]
        xs = [p[0] for p in bbox]
        avg_y = sum(ys) / len(ys)
        min_x = min(xs)
        items.append((avg_y, min_x, text))

    if not items:
        return ""

    items.sort(key=lambda x: (x[0], x[1]))

    # Estimate average line height for merging
    heights = []
    for line in ocr_lines:
        if not line:
            continue
        bbox = line[0]
        ys = [p[1] for p in bbox]
        heights.append(max(ys) - min(ys))
    avg_height = sum(heights) / len(heights) if heights else 20.0

    lines: List[str] = []
    current_line: List[Tuple[float, str]] = []
    last_y = None

    for avg_y, min_x, text in items:
        if last_y is not None and abs(avg_y - last_y) < avg_height * 0.8:
            current_line.append((min_x, text))
        else:
            if current_line:
                current_line.sort(key=lambda x: x[0])
                lines.append(" ".join(t for _, t in current_line))
            current_line = [(min_x, text)]
        last_y = avg_y

    if current_line:
        current_line.sort(key=lambda x: x[0])
        lines.append(" ".join(t for _, t in current_line))

    full_text = " ".join(lines)
    full_text = re.sub(r"\s+", " ", full_text).strip()
    return full_text


def normalize_text(text: str) -> str:
    """Normalize text: full-width ASCII to half-width, compress spaces."""
    result = []
    for ch in text:
        code = ord(ch)
        if 0xFF01 <= code <= 0xFF5E:
            result.append(chr(code - 0xFEE0))
        elif code == 0x3000:
            result.append(" ")
        else:
            result.append(ch)
    text = "".join(result)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _bbox_to_rect(bbox: List[List[float]]) -> Dict[str, float]:
    xs = [p[0] for p in bbox]
    ys = [p[1] for p in bbox]
    return {
        "x": min(xs),
        "y": min(ys),
        "w": max(xs) - min(xs),
        "h": max(ys) - min(ys),
    }


def _extract_snippet(full_text: str, hit_word: str, window: int = 20) -> str:
    idx = full_text.find(hit_word)
    if idx == -1:
        return full_text[: window * 2]
    start = max(0, idx - window)
    end = min(len(full_text), idx + len(hit_word) + window)
    return full_text[start:end]


def extract_fields_from_lines(ocr_lines: List[Any]) -> Tuple[List[Dict[str, Any]], List[str], str]:
    """Extract structured fields from OCR lines, preserving bbox per hit.

    Returns:
        fields: list of field dicts (with bbox)
        tokens: list of extracted token strings
        normalized_text: full normalized text
    """
    raw_text = clean_text(ocr_lines)
    corrected_text, _ = apply_correction(raw_text)
    normalized_text = normalize_text(corrected_text)

    fields: List[Dict[str, Any]] = []
    tokens: List[str] = []

    for line in ocr_lines:
        if not line:
            continue
        bbox = line[0]
        text = line[1][0]
        line_text = normalize_text(apply_correction(text)[0])

        for pattern in RSA_PATTERNS:
            for match in pattern.finditer(line_text):
                value = match.group(1)
                if value:
                    fields.append(
                        {
                            "field": "crypto.rsa.key_length",
                            "value": value,
                            "snippet": _extract_snippet(normalized_text, match.group(0)),
                            "bbox": _bbox_to_rect(bbox),
                            "raw_token": match.group(0),
                        }
                    )
                    tokens.append(match.group(0))

        for pattern in TLS_PATTERNS:
            for match in pattern.finditer(line_text):
                value = match.group(1)
                if value:
                    fields.append(
                        {
                            "field": "crypto.tls.version",
                            "value": value,
                            "snippet": _extract_snippet(normalized_text, match.group(0)),
                            "bbox": _bbox_to_rect(bbox),
                            "raw_token": match.group(0),
                        }
                    )
                    tokens.append(match.group(0))

        for name, pattern in WEAK_ALGO_PATTERNS.items():
            if pattern.search(line_text):
                fields.append(
                    {
                        "field": "crypto.weak",
                        "value": name,
                        "snippet": _extract_snippet(normalized_text, name),
                        "bbox": _bbox_to_rect(bbox),
                        "raw_token": name,
                    }
                )
                tokens.append(name)

    return fields, tokens, normalized_text
