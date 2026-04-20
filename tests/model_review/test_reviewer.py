import json

from src.common.json_io import load_string_map
from src.model_review.reviewer import batch_semantic_review, semantic_review


def test_semantic_review_normalizes_rsa() -> None:
    result = semantic_review({"value": "RSA2048"})
    assert result["normalized"] == "RSA-2048"
    assert float(result["confidence"]) >= 0.9


def test_semantic_review_normalizes_tls() -> None:
    result = semantic_review({"value": "Current protocol is TLS1.2"})
    assert result["normalized"] == "TLS-1.2"


def test_semantic_review_detects_weak_algorithm() -> None:
    result = semantic_review({"value": "hash method: MD5"})
    assert result["normalized"] == "WEAK-ALGO-MD5"


def test_semantic_review_unknown_requires_review() -> None:
    result = semantic_review({"value": "custom security sentence"})
    assert "Requires manual review" in result["explanation"]
    assert result["confidence"] == "0.50"


def test_semantic_review_uses_field_context_for_numeric_values() -> None:
    result = semantic_review({"field": "crypto.rsa.key_length", "value": "2048"})
    assert result["normalized"] == "RSA-2048"
    assert result["policy_hint"] == "s1_rsa_review"


def test_batch_semantic_review_preserves_order() -> None:
    results = batch_semantic_review(
        [
            {"field": "crypto.tls.version", "value": "1.1"},
            {"value": "hash method: MD5"},
        ]
    )
    assert results[0]["normalized"] == "TLS-1.1"
    assert results[1]["normalized"] == "WEAK-ALGO-MD5"


def test_load_fields_accepts_string_path(tmp_path) -> None:
    fields_path = tmp_path / "fields.json"
    fields_path.write_text(json.dumps({"crypto.rsa.key_length": "2048"}), encoding="utf-8")

    result = load_string_map(str(fields_path))

    assert result == {"crypto.rsa.key_length": "2048"}
