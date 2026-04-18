from pathlib import Path
from typing import Any, Dict, List

try:
    from PIL import Image, ImageDraw
except Exception:  # pragma: no cover
    Image = None  # type: ignore
    ImageDraw = None  # type: ignore


def highlight_bbox(image_path: Path, bbox: Dict[str, Any], output_path: Path) -> Path:
    """Draw a red rectangle on the image at the bbox position.

    Args:
        image_path: Path to the original image.
        bbox: dict with x, y, w, h keys.
        output_path: Path to save the highlighted image.

    Returns:
        output_path
    """
    if Image is None:
        raise RuntimeError("PIL (Pillow) is required for highlight_bbox")
    if not image_path.exists():
        raise FileNotFoundError(f"image not found: {image_path}")

    with Image.open(image_path) as img:
        draw = ImageDraw.Draw(img)
        x = bbox.get("x", 0)
        y = bbox.get("y", 0)
        w = bbox.get("w", 0)
        h = bbox.get("h", 0)
        draw.rectangle([x, y, x + w, y + h], outline="#FF0000", width=2)
        img.save(output_path)

    return output_path


def export_evidence_package(
    traces: List[Dict[str, Any]], image_dir: Path, output_dir: Path
) -> Dict[str, Any]:
    """Export a package of evidence with highlighted images.

    Args:
        traces: List of EvidenceTraceV3 dicts.
        image_dir: Directory containing original images.
        output_dir: Directory to save highlighted images.

    Returns:
        Summary dict with export details.
    """
    if Image is None:
        raise RuntimeError("PIL (Pillow) is required for export_evidence_package")

    output_dir.mkdir(parents=True, exist_ok=True)
    exported: List[Dict[str, str]] = []

    for trace in traces:
        image_ref = trace.get("image_ref", "")
        evidence_id = trace.get("evidence_id", "")
        bbox = trace.get("bbox")

        if not image_ref or not bbox:
            exported.append(
                {
                    "evidence_id": evidence_id,
                    "status": "skipped",
                    "reason": "missing image_ref or bbox",
                }
            )
            continue

        image_path = None
        for ext in (".png", ".jpg", ".jpeg", ".ppm", ".pgm"):
            candidate = image_dir / f"{image_ref}{ext}"
            if candidate.exists():
                image_path = candidate
                break

        if not image_path:
            exported.append(
                {
                    "evidence_id": evidence_id,
                    "status": "failed",
                    "reason": f"image file for {image_ref} not found in {image_dir}",
                }
            )
            continue

        out_path = output_dir / f"{evidence_id}_highlight.png"
        try:
            highlight_bbox(image_path, bbox, out_path)
            exported.append(
                {
                    "evidence_id": evidence_id,
                    "status": "success",
                    "highlight_path": str(out_path),
                }
            )
        except Exception as exc:
            exported.append(
                {
                    "evidence_id": evidence_id,
                    "status": "failed",
                    "reason": str(exc),
                }
            )

    return {
        "total": len(traces),
        "exported": len([e for e in exported if e["status"] == "success"]),
        "failed": len([e for e in exported if e["status"] == "failed"]),
        "skipped": len([e for e in exported if e["status"] == "skipped"]),
        "details": exported,
    }
