from src.storage.repository import InMemoryRepository


def test_repository_stores_s2_records_by_task() -> None:
    repo = InMemoryRepository()
    parse_record = {"schema_version": "2.1", "input_type": "pdf"}
    ocr_records = [{"image_id": "img-0001", "page": 1}]
    fields = [{"field": "crypto.rsa.key_length", "value": "2048", "page": 1}]
    traces = [{"field": "crypto.rsa.key_length", "value": "2048", "page": 1}]

    repo.add_parse_record("task-1", parse_record)
    repo.add_ocr_records("task-1", ocr_records)
    repo.add_structured_fields("task-1", fields)
    repo.add_evidence_traces("task-1", traces)

    assert repo.get_parse_record("task-1") == parse_record
    assert repo.get_ocr_records("task-1") == ocr_records
    assert repo.get_structured_fields("task-1") == fields
    assert repo.get_evidence_by_field("task-1", "crypto.rsa.key_length") == traces
    assert repo.get_evidence_by_page("task-1", 1) == traces
