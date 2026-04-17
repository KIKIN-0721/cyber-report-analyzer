import os
import warnings
from pathlib import Path
from typing import Any, Dict, List, Union

from .correction import apply_correction
from .post_processor import clean_text, extract_fields_from_lines

# Suppress PaddleOCR model source connectivity check warnings
os.environ.setdefault("PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK", "True")

_ocr_engine = None


def _normalize_ocr_result(raw_result: Any) -> List[Any]:
    """Normalize various PaddleOCR return formats to internal line format.

    Internal line format: [[bbox, (text, confidence)], ...]
    where bbox = [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
    """
    if not raw_result:
        return []

    if isinstance(raw_result, list) and len(raw_result) > 0:
        first = raw_result[0]
    else:
        return []

    # New PaddleOCR (>=2.10) returns list of OCRResult (dict-like)
    if hasattr(first, "get") or hasattr(first, "keys"):
        ocr_res = first
        rec_texts = ocr_res.get("rec_texts", []) if hasattr(ocr_res, "get") else []
        rec_scores = ocr_res.get("rec_scores", []) if hasattr(ocr_res, "get") else []
        rec_boxes = ocr_res.get("rec_boxes", []) if hasattr(ocr_res, "get") else []
        lines: List[Any] = []
        for i, text in enumerate(rec_texts):
            score = rec_scores[i] if i < len(rec_scores) else 0.0
            box = rec_boxes[i] if i < len(rec_boxes) else []
            if hasattr(box, "tolist"):
                box = box.tolist()
            # box may be [[x1,y1],[x2,y2],[x3,y3],[x4,y4]] or [x1,y1,x2,y2,x3,y3,x4,y4]
            if isinstance(box, (list, tuple)) and len(box) == 4 and isinstance(box[0], (list, tuple)):
                pass  # already 4-point format
            elif isinstance(box, (list, tuple)) and len(box) == 8:
                box = [
                    [float(box[0]), float(box[1])],
                    [float(box[2]), float(box[3])],
                    [float(box[4]), float(box[5])],
                    [float(box[6]), float(box[7])],
                ]
            else:
                box = [[0.0, 0.0], [0.0, 0.0], [0.0, 0.0], [0.0, 0.0]]
            lines.append([box, (text, score)])
        return lines

    # Old format: first element is already list of lines
    if isinstance(first, list):
        return first

    return []


def _get_ocr_engine() -> Any:
    global _ocr_engine
    if _ocr_engine is None:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            from paddleocr import PaddleOCR

            _ocr_engine = PaddleOCR(
                use_angle_cls=True,
                lang="ch",
            )
    return _ocr_engine


def run_ocr(image_path: Path, image_id: str = "", page: int = 0) -> Dict[str, Any]:
    """Run OCR on one image and return OCRResultV2.

    Args:
        image_path: Path to the image file.
        image_id: Identifier for the image (e.g. img-0001).
        page: Page number in the source PDF.

    Returns:
        Dict matching OCRResultV2 protocol with additional fields list.
    """
    if not isinstance(image_path, Path):
        raise TypeError("image_path must be a pathlib.Path")
    if not image_path.exists():
        raise FileNotFoundError(f"image not found: {image_path}")

    engine = _get_ocr_engine()
    raw_result = engine.ocr(str(image_path))

    ocr_lines = _normalize_ocr_result(raw_result)

    fields, tokens, normalized_text = extract_fields_from_lines(ocr_lines)
    raw_text = clean_text(ocr_lines)
    _, correction_type = apply_correction(raw_text)

    confidences = [line[1][1] for line in ocr_lines if line and len(line) > 1]
    confidence = sum(confidences) / len(confidences) if confidences else 0.0

    result: Dict[str, Any] = {
        "image_id": image_id,
        "page": page,
        "raw_text": raw_text,
        "normalized_text": normalized_text,
        "confidence": round(confidence, 4),
        "tokens": tokens,
        "fields": fields,
        "correction_type": correction_type,
    }
    return result


def run_batch_ocr(image_items: Union[List[Path], List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """Run OCR on a batch of images.

    Supports two input formats:
      1. List[Path]: generates sequential image_id and page.
      2. List[Dict]: expects dicts with 'path', 'image_id', 'page' keys.

    Returns:
        List of OCRResultV2 dicts.
    """
    results: List[Dict[str, Any]] = []
    if not image_items:
        return results

    if isinstance(image_items[0], Path):
        for idx, path in enumerate(image_items, start=1):
            image_id = f"img-{idx:04d}"
            page = idx
            results.append(run_ocr(path, image_id=image_id, page=page))
    elif isinstance(image_items[0], dict):
        for item in image_items:
            raw_path = item.get("path")
            if isinstance(raw_path, str):
                path = Path(raw_path)
            elif isinstance(raw_path, Path):
                path = raw_path
            else:
                raise TypeError("image item must contain a 'path' key with Path or str")
            image_id = item.get("image_id", "")
            page = item.get("page", 0)
            results.append(run_ocr(path, image_id=image_id, page=page))
    else:
        raise TypeError("image_items must be List[Path] or List[Dict[str, Any]]")

    return results
