from typing import Any, Dict, List


class InMemoryRepository:
    """Temporary repository used before SQLite integration."""

    def __init__(self) -> None:
        self._items: List[Dict[str, str]] = []
        self._parse_records: Dict[str, Dict[str, Any]] = {}
        self._ocr_records: Dict[str, List[Dict[str, Any]]] = {}
        self._structured_fields: Dict[str, List[Dict[str, Any]]] = {}
        self._evidence_traces: Dict[str, List[Dict[str, Any]]] = {}

    def add(self, item: Dict[str, str]) -> None:
        self._items.append(item)

    def all(self) -> List[Dict[str, str]]:
        return list(self._items)

    def add_parse_record(self, task_id: str, record: Dict[str, Any]) -> None:
        self._parse_records[task_id] = dict(record)

    def get_parse_record(self, task_id: str) -> Dict[str, Any] | None:
        record = self._parse_records.get(task_id)
        return dict(record) if record is not None else None

    def add_ocr_records(self, task_id: str, records: List[Dict[str, Any]]) -> None:
        self._ocr_records.setdefault(task_id, []).extend(dict(record) for record in records)

    def get_ocr_records(self, task_id: str) -> List[Dict[str, Any]]:
        return [dict(record) for record in self._ocr_records.get(task_id, [])]

    def add_structured_fields(self, task_id: str, fields: List[Dict[str, Any]]) -> None:
        self._structured_fields.setdefault(task_id, []).extend(dict(field) for field in fields)

    def get_structured_fields(self, task_id: str) -> List[Dict[str, Any]]:
        return [dict(field) for field in self._structured_fields.get(task_id, [])]

    def add_evidence_traces(self, task_id: str, traces: List[Dict[str, Any]]) -> None:
        self._evidence_traces.setdefault(task_id, []).extend(dict(trace) for trace in traces)

    def get_evidence_traces(self, task_id: str) -> List[Dict[str, Any]]:
        return [dict(trace) for trace in self._evidence_traces.get(task_id, [])]

    def get_evidence_by_field(self, task_id: str, field: str) -> List[Dict[str, Any]]:
        return [trace for trace in self.get_evidence_traces(task_id) if trace.get("field") == field]

    def get_evidence_by_page(self, task_id: str, page: int) -> List[Dict[str, Any]]:
        return [trace for trace in self.get_evidence_traces(task_id) if trace.get("page") == page]
