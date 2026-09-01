import re

INJECTION_PATTERNS = (
    r"ignore\s+(all\s+)?previous instructions",
    r"reveal\s+(the\s+)?system prompt",
    r"override\s+(your\s+)?rules",
)


def contains_prompt_injection(text: str) -> bool:
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in INJECTION_PATTERNS)
