from typing import Any, Dict, List

from src.model_review.reviewer import semantic_review
from src.reporting.report_exporter import export_summary
from src.rules_engine.rule_engine import evaluate_rules, evaluate_s1_baseline


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


def set_task_result(task_id: str, result: Dict[str, Any]) -> Dict[str, Any]:
    """Attach result and move task to completed state."""
    task = get_task(task_id)
    task["result"] = result
    task["status"] = "completed"
    return task


def analyze_task(task_id: str, fields: Dict[str, str], rules: List[Dict[str, str]]) -> Dict[str, Any]:
    """Execute minimal analysis pipeline and store final result on task.

    This function is the backend orchestration entry for S1/S2 integration.
    """
    if not isinstance(fields, dict):
        raise TypeError("fields must be a dict")
    if not isinstance(rules, list):
        raise TypeError("rules must be a list")

    if rules:
        rule_results = evaluate_rules(fields, rules)
    else:
        rule_results = evaluate_s1_baseline(fields)
    review_details: List[Dict[str, str]] = []

    for item in rule_results:
        if item.get("verdict") == "REVIEW":
            review_details.append(
                {
                    "rule_id": item.get("rule_id", ""),
                    **semantic_review({"value": item.get("value", "")}),
                }
            )

    summary = export_summary(rule_results)
    payload: Dict[str, Any] = {
        "task_id": task_id,
        "fields": fields,
        "rule_results": rule_results,
        "review_details": review_details,
        "summary": summary,
    }
    task = set_task_result(task_id, payload)
    return task
