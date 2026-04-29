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
from src.ocr.ocr_pipeline import build_ocr_image_items, run_ocr_for_parse_result


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
        image_items = build_ocr_image_items(parse_result)

        print("Running OCR on extracted images ...")
        ocr_payload = run_ocr_for_parse_result({**parse_result, "images": image_items})

        output = {
            "schema_version": "2.1",
            "pdf_path": str(pdf_path),
            "text_block_count": len(parse_result["text_blocks"]),
            "image_count": len(parse_result["image_paths"]),
            "ocr_results": ocr_payload["ocr_results"],
            "structured_fields": ocr_payload["structured_fields"],
        }

        out_path = pdf_path.with_suffix(".s2_ocr.json")
        out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Results written to {out_path}")
    else:
        print("No images found in PDF.")


if __name__ == "__main__":
    main()
