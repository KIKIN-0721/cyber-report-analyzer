import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.common.json_io import dump_json, load_json_object, write_json_file
from src.rules_engine.s1_field_extractor import S1_CORE_FIELDS


def export_summary(results: List[Dict[str, str]]) -> Dict[str, int]:
    """Build summary counts for PASS/FAIL/REVIEW.

    This is a skeleton API for S4 implementation.
    """
    summary = {"PASS": 0, "FAIL": 0, "REVIEW": 0}
    for item in results:
        verdict = item.get("verdict", "REVIEW")
        if verdict not in summary:
            verdict = "REVIEW"
        summary[verdict] += 1
    return summary


def _extract_results_list(payload: object) -> List[Dict[str, str]]:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("findings", "rule_results", "results"):
            value = payload.get(key)
            if isinstance(value, list):
                return value
    raise ValueError("results file must contain a list or a result envelope")


def export_s1_warnings(parse_payload: Dict[str, object], fields_payload: Dict[str, object]) -> List[str]:
    """Build user-facing warnings for S1 demo evidence."""
    warnings: List[str] = []
    if int(parse_payload.get("parser_text_block_count") or 0) == 0:
        warnings.append(
            "No parser text blocks were found. If this is a scanned PDF, S2 OCR is required."
        )
    if int(parse_payload.get("image_count") or 0) == 0:
        warnings.append("No embedded images were extracted from this PDF.")

    fields = fields_payload.get("fields", {})
    if not isinstance(fields, dict):
        fields = {}
    for field_name in S1_CORE_FIELDS:
        if field_name not in fields:
            warnings.append(f"S1 field not found in PDF text: {field_name}")
    return warnings


def _main() -> None:
    parser = argparse.ArgumentParser(description="Export S1 PASS/FAIL/REVIEW summary.")
    parser.add_argument("--results-file", required=True, type=Path, help="Rule results JSON.")
    parser.add_argument("--parse-file", type=Path, help="Optional parser JSON for warnings.")
    parser.add_argument("--fields-file", type=Path, help="Optional fields JSON for warnings.")
    parser.add_argument("--output", type=Path, help="Optional JSON output path.")
    args = parser.parse_args()

    results = _extract_results_list(load_json_object(args.results_file))
    payload: Dict[str, object] = {"summary": export_summary(results)}
    if args.parse_file and args.fields_file:
        parse_payload = load_json_object(args.parse_file)
        fields_payload = load_json_object(args.fields_file)
        payload["warnings"] = export_s1_warnings(parse_payload, fields_payload)
    text = dump_json(payload)
    if args.output:
        write_json_file(args.output, payload)
    print(text)


if __name__ == "__main__":
    _main()
