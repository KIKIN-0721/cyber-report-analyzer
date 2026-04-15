from src.model_review.reviewer import semantic_review


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
