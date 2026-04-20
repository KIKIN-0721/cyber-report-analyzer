from src.rules_engine.s1_rulebook import get_s1_rulebook


def test_get_s1_rulebook_shape() -> None:
    data = get_s1_rulebook()
    assert data["rulebook_version"] == "S1-RULEBOOK-v0.1"
    assert isinstance(data["rules"], list)
    assert len(data["rules"]) >= 3
    assert isinstance(data["documented_rules"], list)
    assert data["source_document"].endswith("S1-规则台账-v0.1.md")
    rule_ids = {item["rule_id"] for item in data["rules"]}
    assert "S1-RSA-001" in rule_ids
    assert "S1-TLS-001" in rule_ids
    assert "S1-WEAK-001" in rule_ids
    for item in data["rules"]:
        assert item["priority"] == "P0"
        assert item["source_document"].endswith("S1-规则台账-v0.1.md")
        assert item["standard_id"].startswith("标准")
        assert item["check_item"]
