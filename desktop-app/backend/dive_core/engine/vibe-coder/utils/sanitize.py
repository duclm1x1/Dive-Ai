from __future__ import annotations

import re


INJECTION_PATTERNS = [
    r"(?i)ignore (all|previous) instructions",
    r"(?i)system prompt",
    r"(?i)developer message",
    r"(?i)do anything now",
    r"(?i)exfiltrate",
]


def sanitize_untrusted_text(text: str, max_len: int = 20000) -> str:
    t = (text or '')[:max_len]
    # Remove common instruction-hijack markers, keep content for context but reduce directive strength.
    for pat in INJECTION_PATTERNS:
        t = re.sub(pat, '[REDACTED]', t)
    return t
