from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]


def test_s1_field_mapping_deliverable_covers_p0_fields() -> None:
    mapping_path = ROOT / "docs" / "rules" / "field_mapping-v0.1.yaml"
    assert mapping_path.exists()

    data = yaml.safe_load(mapping_path.read_text(encoding="utf-8"))
    fields = {item["field"]: item for item in data["fields"]}

    assert set(fields) >= {
        "crypto.rsa.key_length",
        "crypto.tls.version",
        "crypto.weak",
    }
    for field_name in ("crypto.rsa.key_length", "crypto.tls.version", "crypto.weak"):
        item = fields[field_name]
        assert item["priority"] == "P0"
        assert len(item["aliases"]) >= 6
        assert len(item["extraction_patterns"]) >= 2
        assert item["normalization_rule"]
        assert item["s1_policy"]


def test_s1_sample_case_deliverable_has_at_least_twenty_cases() -> None:
    sample_path = ROOT / "docs" / "rules" / "S1-样本用例设计-v0.1.md"
    assert sample_path.exists()

    text = sample_path.read_text(encoding="utf-8")
    case_count = text.count("| S1-TC-")

    assert case_count >= 20
    assert "crypto.rsa.key_length" in text
    assert "crypto.tls.version" in text
    assert "crypto.weak" in text
