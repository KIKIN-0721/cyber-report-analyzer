import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.common.json_io import dump_json, load_string_map, write_json_file
from src.rules_engine.s1_rulebook import get_s1_rulebook


VERDICTS = {"PASS", "FAIL", "REVIEW"}
WEAK_ALGO_KEYWORDS = ("md5", "sha-1", "des", "3des", "rc4", "ecb")
WEAK_ALGO_PATTERNS = {
    "MD5": re.compile(r"\bmd5\b", re.IGNORECASE),
    "SHA-1": re.compile(r"\bsha[\s_-]?1\b", re.IGNORECASE),
    "DES": re.compile(r"\bdes\b", re.IGNORECASE),
    "3DES": re.compile(r"\b3des\b", re.IGNORECASE),
    "RC4": re.compile(r"\brc4\b", re.IGNORECASE),
    "ECB": re.compile(r"\becb\b", re.IGNORECASE),
}


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


def _build_rule_result(
    rule: Dict[str, Any],
    *,
    field: str,
    value: str,
    verdict: str,
    reason: str,
) -> Dict[str, str]:
    result = {
        "rule_id": str(rule.get("rule_id") or ""),
        "standard_id": str(rule.get("standard_id") or ""),
        "check_item": str(rule.get("check_item") or ""),
        "field": field,
        "value": value,
        "verdict": verdict,
        "reason": reason,
    }
    if rule.get("priority"):
        result["priority"] = str(rule["priority"])
    if rule.get("policy"):
        result["policy"] = str(rule["policy"])
    return result


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
        operator = str(rule.get("operator") or rule.get("op") or "")
        expected = str(rule.get("value") or "")

        if not field:
            results.append(
                _build_rule_result(
                    {"rule_id": rule_id, **rule},
                    field="",
                    value="",
                    verdict="REVIEW",
                    reason="Rule field is missing.",
                )
            )
            continue

        if field not in fields:
            results.append(
                _build_rule_result(
                    {"rule_id": rule_id, **rule},
                    field=field,
                    value="",
                    verdict="REVIEW",
                    reason="Field value is missing in extracted fields.",
                )
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
            _build_rule_result(
                {"rule_id": rule_id, **rule},
                field=field,
                value=actual,
                verdict=verdict,
                reason=reason,
            )
        )

    return results


def classify_review_items(results: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Return REVIEW items for downstream manual or model-assisted handling."""
    if not isinstance(results, list):
        raise TypeError("results must be a list")

    review_items: List[Dict[str, str]] = []
    for item in results:
        if not isinstance(item, dict):
            raise TypeError("each result must be a dict")
        if item.get("verdict") != "REVIEW":
            continue
        review_items.append(
            {
                "rule_id": str(item.get("rule_id") or ""),
                "standard_id": str(item.get("standard_id") or ""),
                "check_item": str(item.get("check_item") or ""),
                "field": str(item.get("field") or ""),
                "value": str(item.get("value") or ""),
                "reason": str(item.get("reason") or ""),
            }
        )

    return review_items


def evaluate_s1_baseline(fields: Dict[str, str]) -> List[Dict[str, str]]:
    """Evaluate S1 P0 baseline rules from the rule ledger.

    Covered checks:
    - RSA key length: >=3072 PASS, ==2048 REVIEW, <2048 FAIL
    - TLS version: >=1.2 PASS, ==1.1 REVIEW, <=1.0 FAIL
    - Weak algorithm keywords: hit -> REVIEW, not hit -> PASS
    """
    if not isinstance(fields, dict):
        raise TypeError("fields must be a dict")

    rulebook = get_s1_rulebook()
    rule_defs = {
        rule["rule_id"]: rule
        for rule in rulebook["rules"]
        if isinstance(rule, dict) and rule.get("rule_id")
    }

    def require_rule(rule_id: str) -> Dict[str, Any]:
        if rule_id not in rule_defs:
            raise KeyError(f"missing S1 rule definition: {rule_id}")
        return rule_defs[rule_id]

    results: List[Dict[str, str]] = []

    # RSA baseline rule
    rsa_rule = require_rule("S1-RSA-001")
    rsa_raw = str(fields.get("crypto.rsa.key_length", "")).strip()
    if not rsa_raw:
        results.append(
            _build_rule_result(
                rsa_rule,
                field="crypto.rsa.key_length",
                value="",
                verdict="REVIEW",
                reason="RSA key length is missing.",
            )
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
            _build_rule_result(
                rsa_rule,
                field="crypto.rsa.key_length",
                value=rsa_raw,
                verdict=verdict,
                reason=reason,
            )
        )

    # TLS baseline rule
    tls_rule = require_rule("S1-TLS-001")
    tls_raw = str(fields.get("crypto.tls.version", "")).strip()
    if not tls_raw:
        results.append(
            _build_rule_result(
                tls_rule,
                field="crypto.tls.version",
                value="",
                verdict="REVIEW",
                reason="TLS version is missing.",
            )
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
            _build_rule_result(
                tls_rule,
                field="crypto.tls.version",
                value=tls_raw,
                verdict=verdict,
                reason=reason,
            )
        )

    # Weak algorithm baseline rule
    weak_rule = require_rule("S1-WEAK-001")
    weak_source = " ".join(
        [
            str(fields.get("crypto.weak", "")),
            str(fields.get("raw_text", "")),
            str(fields.get("text", "")),
        ]
    ).lower()
    hits = [name for name, pattern in WEAK_ALGO_PATTERNS.items() if pattern.search(weak_source)]

    if hits:
        results.append(
            _build_rule_result(
                weak_rule,
                field="crypto.weak",
                value=",".join(hits),
                verdict="REVIEW",
                reason="Weak algorithm keyword detected.",
            )
        )
    else:
        results.append(
            _build_rule_result(
                weak_rule,
                field="crypto.weak",
                value="",
                verdict="PASS",
                reason="No weak algorithm keyword detected.",
            )
        )

    return results


def _load_fields(path: Path) -> Dict[str, str]:
    return load_string_map(path)


def _main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate S1 baseline rules.")
    parser.add_argument("--fields-file", required=True, type=Path, help="JSON fields file.")
    parser.add_argument("--output", type=Path, help="Optional JSON output path.")
    args = parser.parse_args()

    payload = evaluate_s1_baseline(_load_fields(args.fields_file))
    text = dump_json(payload)
    if args.output:
        write_json_file(args.output, payload)
    print(text)


if __name__ == "__main__":
    _main()
