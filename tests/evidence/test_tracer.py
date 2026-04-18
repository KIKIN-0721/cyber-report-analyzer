from src.evidence.tracer import build_evidence_trace, build_evidence_batch, reset_counter


def test_build_evidence_trace_basic() -> None:
    reset_counter()
    hit = {
        "task_id": "task-0001",
        "field": "crypto.rsa.key_length",
        "value": "2048",
        "page": 3,
        "snippet": "RSA2048",
        "source_type": "image_ocr",
        "confidence": "0.91",
    }
    trace = build_evidence_trace(hit)
    assert trace["evidence_id"] == "EVI-task-0001-003-01"
    assert trace["field"] == "crypto.rsa.key_length"
    assert trace["value"] == "2048"
    assert trace["page"] == 3
    assert trace["source_type"] == "image_ocr"


def test_build_evidence_trace_with_bbox() -> None:
    reset_counter()
    hit = {
        "task_id": "task-0001",
        "field": "crypto.tls.version",
        "value": "1.2",
        "page": 1,
        "snippet": "TLS1.2",
        "image_ref": "img-0001",
        "bbox": {"x": 10, "y": 20, "w": 100, "h": 30},
        "source_type": "image_ocr",
        "confidence": 0.95,
    }
    trace = build_evidence_trace(hit)
    assert trace["evidence_id"] == "EVI-task-0001-001-01"
    assert trace["bbox"]["x"] == 10
    assert trace["image_ref"] == "img-0001"


def test_build_evidence_batch() -> None:
    reset_counter("task-0002")
    hits = [
        {
            "task_id": "task-0002",
            "field": "crypto.rsa.key_length",
            "value": "2048",
            "page": 1,
            "snippet": "RSA2048",
            "source_type": "image_ocr",
            "confidence": 0.9,
        },
        {
            "task_id": "task-0002",
            "field": "crypto.tls.version",
            "value": "1.2",
            "page": 1,
            "snippet": "TLS1.2",
            "source_type": "image_ocr",
            "confidence": 0.9,
        },
    ]
    traces = build_evidence_batch(hits)
    assert len(traces) == 2
    assert traces[0]["evidence_id"] == "EVI-task-0002-001-01"
    assert traces[1]["evidence_id"] == "EVI-task-0002-001-02"


def test_reset_counter() -> None:
    reset_counter()
    hit = {
        "task_id": "task-0003",
        "field": "x",
        "value": "1",
        "page": 1,
        "snippet": "x",
        "source_type": "text",
        "confidence": 1.0,
    }
    trace1 = build_evidence_trace(hit)
    assert trace1["evidence_id"] == "EVI-task-0003-001-01"
    reset_counter("task-0003")
    trace2 = build_evidence_trace(hit)
    assert trace2["evidence_id"] == "EVI-task-0003-001-01"
