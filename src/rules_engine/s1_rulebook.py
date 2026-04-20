import argparse
import json
from typing import Any, Dict, List


S1_RULEBOOK_VERSION = "S1-RULEBOOK-v0.1"
S1_RULEBOOK_SOURCE = "docs/rules/S1-规则台账-v0.1.md"

S1_P0_RULES: List[Dict[str, str]] = [
    {
        "rule_id": "S1-RSA-001",
        "standard_id": "标准1.1",
        "check_item": "密钥长度",
        "name": "RSA key length baseline",
        "field": "crypto.rsa.key_length",
        "priority": "P0",
        "policy": ">=3072 PASS, ==2048 REVIEW, <2048 FAIL",
        "patterns": "RSA2048,RSA-2048,2048-bit RSA,RSA3072,RSA-3072,3072-bit RSA",
        "review_strategy": "Review when key length is 2048 or parsing is ambiguous.",
        "source_document": S1_RULEBOOK_SOURCE,
    },
    {
        "rule_id": "S1-TLS-001",
        "standard_id": "标准1.2",
        "check_item": "TLS协议版本",
        "name": "TLS version baseline",
        "field": "crypto.tls.version",
        "priority": "P0",
        "policy": ">=1.2 PASS, ==1.1 REVIEW, <=1.0 FAIL",
        "patterns": "TLS1.0,TLS1.1,TLS1.2,TLS1.3,TLS 1.0,TLS 1.1,TLS 1.2,TLS 1.3",
        "review_strategy": "Review legacy versions or malformed version text.",
        "source_document": S1_RULEBOOK_SOURCE,
    },
    {
        "rule_id": "S1-WEAK-001",
        "standard_id": "标准1.2",
        "check_item": "不合适的加密算法",
        "name": "Weak algorithm keyword baseline",
        "field": "crypto.weak",
        "priority": "P0",
        "policy": "Weak keyword hit => REVIEW, otherwise PASS",
        "patterns": "MD5,SHA-1,DES,3DES,RC4,ECB",
        "review_strategy": "Escalate to manual review once a weak algorithm keyword is found.",
        "source_document": S1_RULEBOOK_SOURCE,
    },
]


S1_P1_RULES: List[Dict[str, str]] = [
    {
        "rule_id": "S1-P1-PORT-001",
        "standard_id": "标准2.1",
        "check_item": "端口与服务暴露",
        "name": "Port service and insecure configuration keywords",
        "field": "network.service",
        "priority": "P1",
        "policy": "Documented in S1 and deferred to S2/S3 implementation.",
        "patterns": "telnet,ftp,23,21,anonymous login,debug interface",
        "review_strategy": "Keep as documentation-only rule in S1.",
        "source_document": S1_RULEBOOK_SOURCE,
    },
    {
        "rule_id": "S1-P1-SIGN-001",
        "standard_id": "标准2.2",
        "check_item": "更新与签名机制",
        "name": "Update and signing mechanism checks",
        "field": "system.update",
        "priority": "P1",
        "policy": "Documented in S1 and deferred to S2/S3 implementation.",
        "patterns": "signature update,secure update,firmware signing",
        "review_strategy": "Keep as documentation-only rule in S1.",
        "source_document": S1_RULEBOOK_SOURCE,
    },
    {
        "rule_id": "S1-P1-AUTH-001",
        "standard_id": "标准2.3",
        "check_item": "认证方式与默认口令",
        "name": "Authentication and default credential checks",
        "field": "auth.default_password",
        "priority": "P1",
        "policy": "Documented in S1 and deferred to S2/S3 implementation.",
        "patterns": "default password,admin/admin,weak password",
        "review_strategy": "Keep as documentation-only rule in S1.",
        "source_document": S1_RULEBOOK_SOURCE,
    },
]


def get_s1_rules_by_priority(priority: str) -> List[Dict[str, str]]:
    """Return one priority slice of the S1 rulebook."""
    normalized = str(priority).strip().upper()
    if normalized == "P0":
        return [dict(rule) for rule in S1_P0_RULES]
    if normalized == "P1":
        return [dict(rule) for rule in S1_P1_RULES]
    raise ValueError(f"unsupported priority: {priority}")


def get_s1_rulebook() -> Dict[str, Any]:
    """Return S1 rulebook metadata used by baseline analysis path."""
    return {
        "rulebook_version": S1_RULEBOOK_VERSION,
        "source_document": S1_RULEBOOK_SOURCE,
        "rules": get_s1_rules_by_priority("P0"),
        "documented_rules": get_s1_rules_by_priority("P1"),
    }


def _main() -> None:
    parser = argparse.ArgumentParser(description="Print the S1 rulebook.")
    parser.add_argument(
        "--priority",
        choices=["P0", "P1"],
        help="Only print rules for one priority.",
    )
    args = parser.parse_args()

    payload: Any
    if args.priority:
        payload = get_s1_rules_by_priority(args.priority)
    else:
        payload = get_s1_rulebook()
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    _main()
