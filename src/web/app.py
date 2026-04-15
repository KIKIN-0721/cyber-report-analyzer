from typing import Any, Dict


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
