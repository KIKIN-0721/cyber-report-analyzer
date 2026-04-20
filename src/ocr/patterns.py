import re

RSA_PATTERNS = [
    re.compile(r"RSA\s*[-_]?(\d{3,4})\b", re.IGNORECASE),
    re.compile(r"\b(\d{3,4})\s*[-_]?\s*bit\s*RSA\b", re.IGNORECASE),
    re.compile(r"Key\s*length\s*:?\s*(\d{3,4})\b", re.IGNORECASE),
]

TLS_PATTERNS = [
    re.compile(r"TLS\s*v?\s*([0-9](?:\.[0-9])?)\b", re.IGNORECASE),
    re.compile(r"SSL\s*v?\s*([0-9](?:\.[0-9])?)\b", re.IGNORECASE),
]

WEAK_ALGO_PATTERNS = {
    "MD5": re.compile(r"\bmd5\b", re.IGNORECASE),
    "SHA-1": re.compile(r"\bsha[\s_-]?1\b", re.IGNORECASE),
    "DES": re.compile(r"\bdes\b", re.IGNORECASE),
    "3DES": re.compile(r"\b3des\b", re.IGNORECASE),
    "RC4": re.compile(r"\brc4\b", re.IGNORECASE),
    "ECB": re.compile(r"\becb\b", re.IGNORECASE),
}
