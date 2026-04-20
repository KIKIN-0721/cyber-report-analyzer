from typing import Any, Dict, List

# In-memory counter for evidence_id generation per (task_id, page)
_evidence_counters: Dict[str, int] = {}


def _generate_evidence_id(task_id: str, page: int) -> str:
    key = f"{task_id}:{page}"
    seq = _evidence_counters.get(key, 0) + 1
    _evidence_counters[key] = seq
    return f"EVI-{task_id}-{page:03d}-{seq:02d}"


def reset_counter(task_id: str = "") -> None:
    """Reset evidence counter for a specific task or globally."""
    global _evidence_counters
    if task_id:
        keys_to_remove = [k for k in _evidence_counters if k.startswith(f"{task_id}:")]
        for k in keys_to_remove:
            del _evidence_counters[k]
    else:
        _evidence_counters = {}


def build_evidence_trace(hit: Dict[str, str]) -> Dict[str, Any]:
    """Bind a result hit to an EvidenceTraceV3 record.

    Input hit should contain:
      - field, value, page, snippet, source_type, confidence
    Optional:
      - task_id, rule_id, image_ref, bbox, correction_type, created_at
    """
    if not isinstance(hit, dict):
        raise TypeError("hit must be a dict")

    task_id = str(hit.get("task_id") or "unknown")
    page = int(hit.get("page", 0))
    evidence_id = _generate_evidence_id(task_id, page)

    trace: Dict[str, Any] = {
        "evidence_id": evidence_id,
        "rule_id": str(hit.get("rule_id") or ""),
        "field": str(hit.get("field") or ""),
        "value": str(hit.get("value") or ""),
        "page": page,
        "snippet": str(hit.get("snippet") or ""),
        "image_ref": str(hit.get("image_ref") or ""),
        "source_type": str(hit.get("source_type") or "image_ocr"),
        "confidence": float(hit.get("confidence", 0.0)) if hit.get("confidence") is not None else 0.0,
        "correction_type": str(hit.get("correction_type") or "none"),
    }

    if hit.get("bbox"):
        trace["bbox"] = hit["bbox"]
    if hit.get("created_at"):
        trace["created_at"] = hit["created_at"]

    return trace


def build_evidence_batch(hits: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """Build evidence traces for a batch of hits."""
    if not isinstance(hits, list):
        raise TypeError("hits must be a list")
    return [build_evidence_trace(h) for h in hits]
