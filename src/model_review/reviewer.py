import re
from typing import Dict, List


WEAK_ALGORITHMS = ("md5", "sha-1", "des", "3des", "rc4", "ecb")
WEAK_ALGORITHM_PATTERNS = {
    "MD5": re.compile(r"\bmd5\b", re.IGNORECASE),
    "SHA-1": re.compile(r"\bsha[\s_-]?1\b", re.IGNORECASE),
    "DES": re.compile(r"\bdes\b", re.IGNORECASE),
    "3DES": re.compile(r"\b3des\b", re.IGNORECASE),
    "RC4": re.compile(r"\brc4\b", re.IGNORECASE),
    "ECB": re.compile(r"\becb\b", re.IGNORECASE),
}


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip())


def _build_response(
    normalized: str,
    explanation: str,
    confidence: str,
    policy_hint: str,
) -> Dict[str, str]:
    return {
        "normalized": normalized,
        "explanation": explanation,
        "confidence": confidence,
        "policy_hint": policy_hint,
    }


def semantic_review(item: Dict[str, str]) -> Dict[str, str]:
    """Run semantic normalization and optional review.

    S1 implementation: normalize common security phrases and provide
    a lightweight confidence score for downstream triage.
    """
    if not isinstance(item, dict):
        raise TypeError("item must be a dict")

    field = _normalize_text(str(item.get("field") or "")).lower()
    raw_value = str(item.get("value") or item.get("raw_text") or item.get("text") or "")
    text = _normalize_text(raw_value)
    lower = text.lower()
    context = " ".join(
        [
            field,
            str(item.get("rule_id") or ""),
            str(item.get("reason") or ""),
            lower,
        ]
    ).lower()

    if not text:
        return _build_response(
            "",
            "No input text. Requires manual review.",
            "0.10",
            "manual_review_required",
        )

    if ("rsa" in context or "key_length" in context) and re.fullmatch(r"\d{3,4}", text):
        return semantic_review({"value": f"RSA{text}"})

    if "tls" in context and re.fullmatch(r"[0-9](?:\.[0-9])?", text):
        return semantic_review({"value": f"TLS{text}"})

    rsa_match = re.search(r"rsa\s*[-_: ]?\s*(\d{3,4})|(?:\b(\d{3,4})\s*[- ]?bit\s*rsa\b)", lower)
    if rsa_match:
        bits_text = rsa_match.group(1) or rsa_match.group(2)
        bits = int(bits_text)
        normalized = f"RSA-{bits}"
        if bits >= 3072:
            explanation = "RSA key length is aligned with stricter baseline (>=3072)."
            confidence = "0.96"
            policy_hint = "s1_rsa_pass"
        elif bits >= 2048:
            explanation = "RSA key length meets minimum baseline but should be reviewed by policy."
            confidence = "0.90"
            policy_hint = "s1_rsa_review"
        else:
            explanation = "RSA key length is weak and should be flagged."
            confidence = "0.95"
            policy_hint = "s1_rsa_fail"
        return _build_response(normalized, explanation, confidence, policy_hint)

    tls_match = re.search(r"\btls\s*v?\s*([0-9](?:\.[0-9])?)\b", lower)
    if tls_match:
        version = tls_match.group(1)
        normalized = f"TLS-{version}"
        confidence = "0.95"
        if version in ("1.0", "1.1"):
            explanation = "Legacy TLS version detected and should be reviewed."
            policy_hint = "s1_tls_review"
        else:
            explanation = "TLS version extracted successfully."
            policy_hint = "s1_tls_pass"
        return _build_response(normalized, explanation, confidence, policy_hint)

    for weak_name, pattern in WEAK_ALGORITHM_PATTERNS.items():
        if pattern.search(lower):
            normalized = f"WEAK-ALGO-{weak_name.upper()}"
            return _build_response(
                normalized,
                "Weak cryptographic algorithm keyword detected.",
                "0.92",
                "manual_review_required",
            )

    return _build_response(
        text,
        "No deterministic normalization rule matched. Requires manual review.",
        "0.50",
        "manual_review_required",
    )


def batch_semantic_review(items: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Normalize a batch of review items while preserving input order."""
    if not isinstance(items, list):
        raise TypeError("items must be a list")

    results: List[Dict[str, str]] = []
    for item in items:
        if not isinstance(item, dict):
            raise TypeError("each item must be a dict")
        results.append(semantic_review(item))
    return results
