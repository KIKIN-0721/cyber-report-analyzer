from src.ocr.correction import apply_correction
from src.ocr.post_processor import (
    clean_text,
    extract_fields_from_lines,
    normalize_text,
    _extract_snippet,
)


def test_clean_text_simple() -> None:
    ocr_result = [
        [[[10, 10], [50, 10], [50, 30], [10, 30]], ("TLS1.2", 0.95)],
        [[[10, 35], [60, 35], [60, 55], [10, 55]], ("RSA2048", 0.92)],
    ]
    text = clean_text(ocr_result)
    assert "TLS1.2" in text
    assert "RSA2048" in text


def test_extract_fields_rsa() -> None:
    ocr_lines = [
        [[[0, 0], [100, 0], [100, 20], [0, 20]], ("The device uses RSA2048 for encryption.", 0.95)],
    ]
    fields, tokens, normalized = extract_fields_from_lines(ocr_lines)
    assert len(fields) == 1
    assert fields[0]["field"] == "crypto.rsa.key_length"
    assert fields[0]["value"] == "2048"
    assert "bbox" in fields[0]
    assert "RSA2048" in tokens


def test_extract_fields_tls() -> None:
    ocr_lines = [
        [[[0, 0], [200, 0], [200, 20], [0, 20]], ("Supported TLS 1.2 and TLS 1.3", 0.95)],
    ]
    fields, tokens, normalized = extract_fields_from_lines(ocr_lines)
    tls_fields = [f for f in fields if f["field"] == "crypto.tls.version"]
    assert len(tls_fields) == 2
    assert tls_fields[0]["value"] == "1.2"
    assert tls_fields[1]["value"] == "1.3"


def test_extract_fields_weak_algo() -> None:
    ocr_lines = [
        [[[0, 0], [200, 0], [200, 20], [0, 20]], ("This implementation uses MD5 and SHA1 hashing.", 0.95)],
    ]
    fields, tokens, normalized = extract_fields_from_lines(ocr_lines)
    weak_fields = [f for f in fields if f["field"] == "crypto.weak"]
    values = {f["value"] for f in weak_fields}
    assert "MD5" in values


def test_normalize_text() -> None:
    assert normalize_text("TLS　1．2") == "TLS 1.2"
    assert normalize_text("  RSA   2048  ") == "RSA 2048"


def test_snippet() -> None:
    text = "The device is configured with RSA2048 key length for all TLS sessions."
    snippet = _extract_snippet(text, "RSA2048")
    assert "RSA2048" in snippet


def test_correction() -> None:
    corrected, ctype = apply_correction("TSL 1.2")
    assert "TLS" in corrected
    assert ctype == "dict"
