from typing import Dict, List


VERDICTS = {"PASS", "FAIL", "REVIEW"}


def evaluate_rules(fields: Dict[str, str], rules: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Evaluate structured fields against configured rules.

    This is a skeleton API for S3 implementation.
    """
    if not isinstance(fields, dict):
        raise TypeError("fields must be a dict")
    if not isinstance(rules, list):
        raise TypeError("rules must be a list")

    return []
