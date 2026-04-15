from typing import Dict


def build_evidence_trace(hit: Dict[str, str]) -> Dict[str, str]:
    """Bind result to page, text snippet, and image reference.

    This is a skeleton API for S3-S4 implementation.
    """
    if not isinstance(hit, dict):
        raise TypeError("hit must be a dict")

    return {
        "field": "",
        "value": "",
        "page": "",
        "snippet": "",
        "image_ref": "",
    }
