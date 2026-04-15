from datetime import datetime, timezone
from typing import Any, Dict, List
from uuid import uuid4

from src.model_review.reviewer import batch_semantic_review
from src.reporting.report_exporter import export_summary
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
        "pending_reviews": pending_reviews,
        "review_details": review_details,
        "summary": summary,
    }
    task = set_task_result(task_id, payload)
    return task
