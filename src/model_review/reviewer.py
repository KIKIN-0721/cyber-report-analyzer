import re
from typing import Dict


WEAK_ALGORITHMS = ("md5", "sha-1", "des", "3des", "rc4", "ecb")


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip())


def semantic_review(item: Dict[str, str]) -> Dict[str, str]:
    """Run semantic normalization and optional review.

    S1 implementation: normalize common security phrases and provide
    a lightweight confidence score for downstream triage.
    """
    if not isinstance(item, dict):
        raise TypeError("item must be a dict")

    raw_value = str(item.get("value") or item.get("raw_text") or item.get("text") or "")
    text = _normalize_text(raw_value)
    lower = text.lower()

    if not text:
        return {
            "normalized": "",
            "explanation": "No input text. Requires manual review.",
            "confidence": "0.10",
        }

    rsa_match = re.search(r"rsa\s*[-_: ]?\s*(\d{3,4})|(?:\b(\d{3,4})\s*[- ]?bit\s*rsa\b)", lower)
    if rsa_match:
        bits_text = rsa_match.group(1) or rsa_match.group(2)
        bits = int(bits_text)
        normalized = f"RSA-{bits}"
        if bits >= 3072:
            explanation = "RSA key length is aligned with stricter baseline (>=3072)."
            confidence = "0.96"
        elif bits >= 2048:
            explanation = "RSA key length meets minimum baseline but should be reviewed by policy."
            confidence = "0.90"
        else:
            explanation = "RSA key length is weak and should be flagged."
            confidence = "0.95"
        return {
            "normalized": normalized,
            "explanation": explanation,
            "confidence": confidence,
        }

    tls_match = re.search(r"\btls\s*([0-9](?:\.[0-9])?)\b", lower)
    if tls_match:
        version = tls_match.group(1)
        normalized = f"TLS-{version}"
        confidence = "0.95"
        if version in ("1.0", "1.1"):
            explanation = "Legacy TLS version detected and should be reviewed."
        else:
            explanation = "TLS version extracted successfully."
        return {
            "normalized": normalized,
            "explanation": explanation,
            "confidence": confidence,
        }

    for weak_name in WEAK_ALGORITHMS:
        if weak_name in lower:
            normalized = f"WEAK-ALGO-{weak_name.upper()}"
            return {
                "normalized": normalized,
                "explanation": "Weak cryptographic algorithm keyword detected.",
                "confidence": "0.92",
            }

    return {
        "normalized": text,
        "explanation": "No deterministic normalization rule matched. Requires manual review.",
        "confidence": "0.50",
    }
