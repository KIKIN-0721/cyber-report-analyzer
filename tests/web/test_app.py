from src.web.app import get_task, health, set_task_result, submit_report


def test_health_endpoint() -> None:
    assert health() == {"status": "ok"}


def test_submit_and_query_task() -> None:
    task = submit_report("sample-report.pdf")
    loaded = get_task(task["task_id"])
    assert loaded["file_name"] == "sample-report.pdf"
    assert loaded["status"] == "queued"


def test_set_task_result_marks_completed() -> None:
    task = submit_report("report-2.pdf")
    updated = set_task_result(task["task_id"], {"summary": "ok"})
    assert updated["status"] == "completed"
    assert updated["result"] == {"summary": "ok"}
