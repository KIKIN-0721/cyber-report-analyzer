#!/usr/bin/env python3
"""S2 Parser-OCR Bridge: extract images from PDF and run OCR.

Usage:
    python scripts/s2_parser_ocr_bridge.py <pdf_path>
"""

import json
import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.parser.pdf_parser import extract_text_and_images
from src.ocr.ocr_pipeline import run_batch_ocr


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <pdf_path>")
        sys.exit(1)

    pdf_path = Path(sys.argv[1])
    if not pdf_path.exists():
        print(f"Error: file not found {pdf_path}")
        sys.exit(1)

    print(f"Parsing {pdf_path} ...")
    parse_result = extract_text_and_images(pdf_path)

    print(f"Text blocks: {len(parse_result['text_blocks'])}")
    print(f"Images: {len(parse_result['image_paths'])}")

    if parse_result["image_paths"]:
        # Build image items compatible with run_batch_ocr dict format
        image_items = []
        for idx, img_path in enumerate(parse_result["image_paths"], start=1):
            image_items.append(
                {
                    "path": img_path,
                    "image_id": f"img-{idx:04d}",
                    "page": idx,  # fallback: sequential page numbering
                }
            )

        print("Running OCR on extracted images ...")
        ocr_results = run_batch_ocr(image_items)

        # Aggregate structured fields
        all_fields = []
        for ocr_res in ocr_results:
            for field in ocr_res.get("fields", []):
                all_fields.append(
                    {
                        "field": field["field"],
                        "value": field["value"],
                        "source_type": "image_ocr",
                        "page": ocr_res["page"],
                        "snippet": field["snippet"],
                        "confidence": ocr_res["confidence"],
                        "image_ref": ocr_res["image_id"],
                        "bbox": field.get("bbox"),
                    }
                )

        output = {
            "schema_version": "2.0",
            "pdf_path": str(pdf_path),
            "text_block_count": len(parse_result["text_blocks"]),
            "image_count": len(parse_result["image_paths"]),
            "ocr_results": ocr_results,
            "structured_fields": all_fields,
        }

        out_path = pdf_path.with_suffix(".s2_ocr.json")
        out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Results written to {out_path}")
    else:
        print("No images found in PDF.")


if __name__ == "__main__":
    main()
