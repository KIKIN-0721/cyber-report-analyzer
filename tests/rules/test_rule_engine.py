from src.rules_engine.rule_engine import classify_review_items, evaluate_rules, evaluate_s1_baseline


def test_evaluate_rules_returns_list() -> None:
    result = evaluate_rules(fields={}, rules=[])
    assert isinstance(result, list)


def test_evaluate_rules_numeric_comparison() -> None:
    fields = {"crypto.rsa.key_length": "2048"}
    rules = [
        {
            "rule_id": "R-RSA-001",
            "field": "crypto.rsa.key_length",
            "operator": ">=",
            "value": "3072",
        }
    ]
    result = evaluate_rules(fields=fields, rules=rules)
    assert result[0]["rule_id"] == "R-RSA-001"
    assert result[0]["verdict"] == "FAIL"


def test_evaluate_rules_missing_field_is_review() -> None:
    fields = {}
    rules = [
        {
            "rule_id": "R-TLS-001",
            "field": "crypto.tls.version",
            "operator": "==",
            "value": "1.2",
        }
    ]
    result = evaluate_rules(fields=fields, rules=rules)
    assert result[0]["verdict"] == "REVIEW"


def test_evaluate_rules_contains_pass() -> None:
    fields = {"crypto.weak": "algorithm md5 found"}
    rules = [
        {
            "rule_id": "R-WEAK-001",
            "field": "crypto.weak",
            "operator": "contains",
            "value": "md5",
        }
    ]
    result = evaluate_rules(fields=fields, rules=rules)
    assert result[0]["verdict"] == "PASS"


def test_evaluate_rules_supports_op_alias() -> None:
    fields = {"crypto.tls.version": "1.2"}
    rules = [
        {
            "rule_id": "R-TLS-ALIAS-001",
            "field": "crypto.tls.version",
            "op": "==",
            "value": "1.2",
            "priority": "P0",
        }
    ]
    result = evaluate_rules(fields=fields, rules=rules)
    assert result[0]["verdict"] == "PASS"
    assert result[0]["priority"] == "P0"


def test_evaluate_s1_baseline_rsa_review_tls_pass_weak_review() -> None:
    fields = {
        "crypto.rsa.key_length": "2048",
        "crypto.tls.version": "1.2",
        "raw_text": "detected md5 in report",
    }
    results = evaluate_s1_baseline(fields)
    verdicts = {item["rule_id"]: item["verdict"] for item in results}
    assert verdicts["S1-RSA-001"] == "REVIEW"
    assert verdicts["S1-TLS-001"] == "PASS"
    assert verdicts["S1-WEAK-001"] == "REVIEW"


def test_evaluate_s1_baseline_rsa_fail_tls_fail_weak_pass() -> None:
    fields = {
        "crypto.rsa.key_length": "1024",
        "crypto.tls.version": "1.0",
        "raw_text": "no weak keyword",
    }
    results = evaluate_s1_baseline(fields)
    verdicts = {item["rule_id"]: item["verdict"] for item in results}
    assert verdicts["S1-RSA-001"] == "FAIL"
    assert verdicts["S1-TLS-001"] == "FAIL"
    assert verdicts["S1-WEAK-001"] == "PASS"


def test_classify_review_items_filters_review_results() -> None:
    results = [
        {"rule_id": "A", "field": "one", "value": "1", "verdict": "PASS", "reason": "ok"},
        {"rule_id": "B", "field": "two", "value": "2", "verdict": "REVIEW", "reason": "check"},
    ]
    reviews = classify_review_items(results)
    assert reviews == [{"rule_id": "B", "field": "two", "value": "2", "reason": "check"}]
