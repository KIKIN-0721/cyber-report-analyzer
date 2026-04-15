import re
from typing import Dict, List


VERDICTS = {"PASS", "FAIL", "REVIEW"}
WEAK_ALGO_KEYWORDS = ("md5", "sha-1", "des", "3des", "rc4", "ecb")


def _to_float(value: str) -> float:
    return float(str(value).strip())


def _evaluate(operator: str, actual: str, expected: str) -> bool:
    operator = operator.strip()

    if operator in {">", ">=", "<", "<="}:
        left = _to_float(actual)
        right = _to_float(expected)
        if operator == ">":
            return left > right
        if operator == ">=":
            return left >= right
        if operator == "<":
            return left < right
        return left <= right

    if operator == "==":
        return str(actual).strip().lower() == str(expected).strip().lower()
    if operator == "!=":
        return str(actual).strip().lower() != str(expected).strip().lower()
    if operator == "contains":
        return str(expected).strip().lower() in str(actual).strip().lower()
    if operator == "not_contains":
        return str(expected).strip().lower() not in str(actual).strip().lower()

    raise ValueError(f"unsupported operator: {operator}")


def evaluate_rules(fields: Dict[str, str], rules: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Evaluate structured fields against configured rules.

    Rule format:
    - rule_id: unique rule id
    - field: source key in fields
    - operator: one of >, >=, <, <=, ==, !=, contains, not_contains
    - value: expected value for comparison
    """
    if not isinstance(fields, dict):
        raise TypeError("fields must be a dict")
    if not isinstance(rules, list):
        raise TypeError("rules must be a list")

    results: List[Dict[str, str]] = []

    for index, rule in enumerate(rules, start=1):
        if not isinstance(rule, dict):
            raise TypeError("each rule must be a dict")

        rule_id = str(rule.get("rule_id") or f"RULE-{index:03d}")
        field = str(rule.get("field") or "")
        operator = str(rule.get("operator") or "")
        expected = str(rule.get("value") or "")

        if not field:
            results.append(
                {
                    "rule_id": rule_id,
                    "field": "",
                    "value": "",
                    "verdict": "REVIEW",
                    "reason": "Rule field is missing.",
                }
            )
            continue

        if field not in fields:
            results.append(
                {
                    "rule_id": rule_id,
                    "field": field,
                    "value": "",
                    "verdict": "REVIEW",
                    "reason": "Field value is missing in extracted fields.",
                }
            )
            continue

        actual = str(fields[field])

        try:
            matched = _evaluate(operator, actual, expected)
            verdict = "PASS" if matched else "FAIL"
            reason = f"Rule comparison {actual} {operator} {expected} -> {matched}."
        except ValueError as ex:
            verdict = "REVIEW"
            reason = str(ex)
        except Exception:
            verdict = "REVIEW"
            reason = "Rule evaluation failed and requires manual review."

        results.append(
            {
                "rule_id": rule_id,
                "field": field,
                "value": actual,
                "verdict": verdict,
                "reason": reason,
            }
        )

    return results


def evaluate_s1_baseline(fields: Dict[str, str]) -> List[Dict[str, str]]:
    """Evaluate S1 P0 baseline rules from the rule ledger.

    Covered checks:
    - RSA key length: >=3072 PASS, ==2048 REVIEW, <2048 FAIL
    - TLS version: >=1.2 PASS, ==1.1 REVIEW, <=1.0 FAIL
    - Weak algorithm keywords: hit -> REVIEW, not hit -> PASS
    """
    if not isinstance(fields, dict):
        raise TypeError("fields must be a dict")

    results: List[Dict[str, str]] = []

    # RSA baseline rule
    rsa_raw = str(fields.get("crypto.rsa.key_length", "")).strip()
    if not rsa_raw:
        results.append(
            {
                "rule_id": "S1-RSA-001",
                "field": "crypto.rsa.key_length",
                "value": "",
                "verdict": "REVIEW",
                "reason": "RSA key length is missing.",
            }
        )
    else:
        try:
            rsa_bits = int(float(rsa_raw))
            if rsa_bits >= 3072:
                verdict = "PASS"
                reason = "RSA key length is >= 3072."
            elif rsa_bits == 2048:
                verdict = "REVIEW"
                reason = "RSA 2048 requires policy review in S1 baseline."
            else:
                verdict = "FAIL"
                reason = "RSA key length is < 2048."
        except Exception:
            verdict = "REVIEW"
            reason = "RSA key length format is invalid."

        results.append(
            {
                "rule_id": "S1-RSA-001",
                "field": "crypto.rsa.key_length",
                "value": rsa_raw,
                "verdict": verdict,
                "reason": reason,
            }
        )

    # TLS baseline rule
    tls_raw = str(fields.get("crypto.tls.version", "")).strip()
    if not tls_raw:
        results.append(
            {
                "rule_id": "S1-TLS-001",
                "field": "crypto.tls.version",
                "value": "",
                "verdict": "REVIEW",
                "reason": "TLS version is missing.",
            }
        )
    else:
        match = re.search(r"([0-9](?:\.[0-9])?)", tls_raw)
        if not match:
            verdict = "REVIEW"
            reason = "TLS version format is invalid."
        else:
            tls_num = float(match.group(1))
            if tls_num >= 1.2:
                verdict = "PASS"
                reason = "TLS version is >= 1.2."
            elif tls_num == 1.1:
                verdict = "REVIEW"
                reason = "TLS 1.1 is legacy and requires review."
            else:
                verdict = "FAIL"
                reason = "TLS 1.0 or below is insecure."

        results.append(
            {
                "rule_id": "S1-TLS-001",
                "field": "crypto.tls.version",
                "value": tls_raw,
                "verdict": verdict,
                "reason": reason,
            }
        )

    # Weak algorithm baseline rule
    weak_source = " ".join(
        [
            str(fields.get("crypto.weak", "")),
            str(fields.get("raw_text", "")),
            str(fields.get("text", "")),
        ]
    ).lower()
    hits = [name.upper() for name in WEAK_ALGO_KEYWORDS if name in weak_source]

    if hits:
        results.append(
            {
                "rule_id": "S1-WEAK-001",
                "field": "crypto.weak",
                "value": ",".join(hits),
                "verdict": "REVIEW",
                "reason": "Weak algorithm keyword detected.",
            }
        )
    else:
        results.append(
            {
                "rule_id": "S1-WEAK-001",
                "field": "crypto.weak",
                "value": "",
                "verdict": "PASS",
                "reason": "No weak algorithm keyword detected.",
            }
        )

    return results
