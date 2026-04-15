from src.web.app import (
    analyze_task,
    get_pending_reviews,
    get_task,
    get_task_result,
    health,
    set_task_result,
    submit_report,
)


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
    assert get_task_result(task["task_id"]) == {"summary": "ok"}


def test_analyze_task_pipeline() -> None:
    task = submit_report("report-3.pdf")
    fields = {"crypto.rsa.key_length": "2048", "crypto.tls.version": "1.2"}
    rules = [
        {
            "rule_id": "R-RSA-001",
            "field": "crypto.rsa.key_length",
            "operator": ">=",
            "value": "3072",
        },
        {
            "rule_id": "R-TLS-001",
            "field": "crypto.tls.version",
            "operator": "==",
            "value": "1.2",
        },
    ]

    updated = analyze_task(task["task_id"], fields, rules)
    assert updated["status"] == "completed"
    assert updated["result"]["schema_version"] == "s1.v1"
    assert updated["result"]["rulebook_version"] == "custom"
    assert updated["result"]["trace_id"].startswith("trace-")
    assert updated["result"]["summary"]["PASS"] == 1
    assert updated["result"]["summary"]["FAIL"] == 1


def test_analyze_task_uses_s1_baseline_when_rules_empty() -> None:
    task = submit_report("report-4.pdf")
    fields = {
        "crypto.rsa.key_length": "2048",
        "crypto.tls.version": "1.1",
        "raw_text": "contains md5",
    }

    updated = analyze_task(task["task_id"], fields, [])
    assert updated["status"] == "completed"
    assert updated["result"]["schema_version"] == "s1.v1"
    assert updated["result"]["rulebook_version"] == "S1-RULEBOOK-v0.1"
    assert updated["result"]["trace_id"].startswith("trace-")
    summary = updated["result"]["summary"]
    assert summary["PASS"] == 0
    assert summary["FAIL"] == 0
    assert summary["REVIEW"] == 3
    pending = get_pending_reviews(task["task_id"])
    assert len(pending) == 3
    review_details = updated["result"]["review_details"]
    assert review_details[0]["normalized"] == "RSA-2048"
    assert any(item["normalized"] == "TLS-1.1" for item in review_details)
