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
        text, confidence = line[1]
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
                            "confidence": round(float(confidence), 4),
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
                            "confidence": round(float(confidence), 4),
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
                        "confidence": round(float(confidence), 4),
                    }
                )
                tokens.append(name)

    return fields, tokens, normalized_text


def build_structured_fields_from_ocr(
    ocr_results: List[Dict[str, Any]], input_type: str = "pdf"
) -> List[Dict[str, Any]]:
    """Convert OCRResultV2 records into S2 StructuredField records.

    The OCR layer keeps PaddleOCR-specific details such as bbox and raw_token
    for evidence tracing, while always emitting the stable S2 fields consumed
    by rules and storage.
    """
    structured_fields: List[Dict[str, Any]] = []

    for result in ocr_results:
        page = int(result.get("page", 0) or 0)
        source_type = str(result.get("source_type") or "image_ocr")
        image_id = str(result.get("image_id") or "")
        section_id = str(result.get("section_id") or "")
        paragraph_id = str(result.get("paragraph_id") or "")
        result_confidence = float(result.get("confidence", 0.0) or 0.0)
        result_input_type = str(result.get("input_type") or input_type)

        for field_hit in result.get("fields", []):
            confidence = float(field_hit.get("confidence", result_confidence) or 0.0)
            structured: Dict[str, Any] = {
                "field": str(field_hit.get("field") or ""),
                "value": str(field_hit.get("value") or ""),
                "source_type": source_type,
                "input_type": result_input_type,
                "page": page,
                "section_id": section_id,
                "paragraph_id": paragraph_id,
                "snippet": str(field_hit.get("snippet") or ""),
                "confidence": round(confidence, 4),
                "source_ref": image_id,
            }

            # Evidence-facing extensions are intentionally preserved for S3/S4.
            if field_hit.get("bbox") is not None:
                structured["bbox"] = field_hit["bbox"]
            if field_hit.get("raw_token") is not None:
                structured["raw_token"] = field_hit["raw_token"]
            if result.get("correction_type") is not None:
                structured["correction_type"] = result["correction_type"]

            structured_fields.append(structured)

    return structured_fields
