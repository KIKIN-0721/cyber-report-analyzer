from typing import Dict, List


def export_summary(results: List[Dict[str, str]]) -> Dict[str, int]:
    """Build summary counts for PASS/FAIL/REVIEW.

    This is a skeleton API for S4 implementation.
    """
    summary = {"PASS": 0, "FAIL": 0, "REVIEW": 0}
    for item in results:
        verdict = item.get("verdict", "REVIEW")
        if verdict not in summary:
            verdict = "REVIEW"
        summary[verdict] += 1
    return summary
