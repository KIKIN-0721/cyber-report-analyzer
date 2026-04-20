from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, List

if __package__ in (None, ""):
    ROOT = Path(__file__).resolve().parents[2]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

from src.common.json_io import dump_json, load_json_object, write_json_file
from src.ocr.patterns import RSA_PATTERNS, TLS_PATTERNS, WEAK_ALGO_PATTERNS


S1_CORE_FIELDS = ("crypto.rsa.key_length", "crypto.tls.version", "crypto.weak")


def extract_s1_fields_from_text(text_blocks: List[str]) -> Dict[str, str]:
    """Extract S1 P0 fields from parser text blocks."""
    combined_text = "\n".join(str(item) for item in text_blocks)
    fields: Dict[str, str] = {}

    for pattern in RSA_PATTERNS:
        match = pattern.search(combined_text)
        if match:
            fields["crypto.rsa.key_length"] = match.group(1)
            break

    for pattern in TLS_PATTERNS:
        tls_match = pattern.search(combined_text)
        if tls_match:
            fields["crypto.tls.version"] = tls_match.group(1)
            break

    weak_hits = [
        name for name, pattern in WEAK_ALGO_PATTERNS.items() if pattern.search(combined_text)
    ]
    if weak_hits:
        fields["crypto.weak"] = ",".join(weak_hits)

    fields["raw_text"] = combined_text
    return fields


def _load_text_blocks(parse_file: Path) -> List[str]:
    payload = load_json_object(parse_file)
    if "parser_text_blocks_full" in payload:
        return list(payload["parser_text_blocks_full"])
    if "selected_text_blocks_full" in payload:
        return list(payload["selected_text_blocks_full"])
    if "text_blocks" in payload:
        return list(payload["text_blocks"])
    return []


def _main() -> None:
    parser = argparse.ArgumentParser(description="Extract S1 fields from parser JSON output.")
    parser.add_argument("--parse-file", required=True, type=Path, help="JSON from pdf_parser.py.")
    parser.add_argument("--output", type=Path, help="Optional JSON output path.")
    args = parser.parse_args()

    fields = extract_s1_fields_from_text(_load_text_blocks(args.parse_file))
    payload = {
        "fields": fields,
        "field_count": len([key for key in fields if key != "raw_text"]),
    }
    text = dump_json(payload)
    if args.output:
        write_json_file(args.output, payload)
    print(text)


if __name__ == "__main__":
    _main()
