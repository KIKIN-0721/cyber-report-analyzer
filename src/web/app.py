import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.common.json_io import dump_json, load_string_map, write_json_file
from src.model_review.reviewer import batch_semantic_review
from src.reporting.report_exporter import export_summary
from src.rules_engine.s1_field_extractor import S1_CORE_FIELDS
from src.rules_engine.rule_engine import classify_review_items, evaluate_rules, evaluate_s1_baseline
from src.rules_engine.s1_rulebook import get_s1_rulebook


_TASKS: Dict[str, Dict[str, Any]] = {}


def health() -> Dict[str, str]:
    """Lightweight health endpoint placeholder for web integration."""
    return {"status": "ok"}


def submit_report(file_name: str) -> Dict[str, Any]:
    """Create an analysis task for an uploaded report file."""
    if not file_name or not isinstance(file_name, str):
        raise ValueError("file_name must be a non-empty string")

    task_id = f"task-{len(_TASKS) + 1:04d}"
    task = {
        "task_id": task_id,
        "file_name": file_name,
        "status": "queued",
        "result": None,
    }
    _TASKS[task_id] = task
    return task


def get_task(task_id: str) -> Dict[str, Any]:
    """Get one task by id."""
    if task_id not in _TASKS:
        raise KeyError(f"task not found: {task_id}")
    return _TASKS[task_id]


def get_task_result(task_id: str) -> Dict[str, Any] | None:
    """Return the analysis result payload for one task."""
    return get_task(task_id)["result"]


def set_task_result(task_id: str, result: Dict[str, Any]) -> Dict[str, Any]:
    """Attach result and move task to completed state."""
    task = get_task(task_id)
    task["result"] = result
    task["status"] = "completed"
    return task


def get_pending_reviews(task_id: str) -> List[Dict[str, str]]:
    """Return REVIEW items that need manual or model-assisted follow-up."""
    result = get_task_result(task_id)
    if not result:
        return []
    pending = result.get("pending_reviews", [])
    return pending if isinstance(pending, list) else []


def analyze_task(task_id: str, fields: Dict[str, str], rules: List[Dict[str, str]]) -> Dict[str, Any]:
    """Execute minimal analysis pipeline and store final result on task.

    This function is the backend orchestration entry for S1/S2 integration.
    """
    if not isinstance(fields, dict):
        raise TypeError("fields must be a dict")
    if not isinstance(rules, list):
        raise TypeError("rules must be a list")

    rulebook_version = "custom"
    if rules:
        rule_results = evaluate_rules(fields, rules)
    else:
        rulebook_version = str(get_s1_rulebook()["rulebook_version"])
        rule_results = evaluate_s1_baseline(fields)
    pending_reviews = classify_review_items(rule_results)
    normalized_reviews = batch_semantic_review(pending_reviews)
    review_details: List[Dict[str, str]] = []
    for pending, normalized in zip(pending_reviews, normalized_reviews):
        review_details.append({**pending, **normalized})

    summary = export_summary(rule_results)
    payload: Dict[str, Any] = {
        "schema_version": "s1.v1",
        "trace_id": f"trace-{uuid4().hex[:12]}",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "rulebook_version": rulebook_version,
        "task_id": task_id,
        "fields": fields,
        "rule_results": rule_results,
        "findings": rule_results,
        "pending_reviews": pending_reviews,
        "review_details": review_details,
        "summary": summary,
    }
    task = set_task_result(task_id, payload)
    return task


def _load_fields(path: Path) -> Dict[str, str]:
    return load_string_map(path)


def _main() -> None:
    parser = argparse.ArgumentParser(description="Run the S1 backend task loop.")
    parser.add_argument("--file-name", help="Original report file name.")
    parser.add_argument("--pdf-path", type=Path, help="Original report PDF path.")
    parser.add_argument("--fields-file", required=True, type=Path, help="JSON fields file.")
    parser.add_argument("--output", type=Path, help="Optional JSON output path.")
    args = parser.parse_args()

    file_name = args.file_name or (args.pdf_path.name if args.pdf_path else "")
    task = submit_report(file_name)
    completed = analyze_task(task["task_id"], _load_fields(args.fields_file), [])
    compact = {
        "task_id": completed.get("task_id"),
        "file_name": completed.get("file_name"),
        "status": completed.get("status"),
        "summary": (completed.get("result") or {}).get("summary"),
        "pending_reviews": (completed.get("result") or {}).get("pending_reviews"),
        "findings": (completed.get("result") or {}).get("findings"),
        "result": completed.get("result"),
    }
    text = dump_json(compact)
    if args.output:
        write_json_file(args.output, compact)
    print(text)


if __name__ == "__main__":
    _main()
