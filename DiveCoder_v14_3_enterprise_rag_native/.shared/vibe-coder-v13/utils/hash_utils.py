from __future__ import annotations

import hashlib
from pathlib import Path


def sha256_text(text: str) -> str:
    h = hashlib.sha256()
    h.update(text.encode('utf-8', errors='ignore'))
    return h.hexdigest()


def sha256_file(path: str | Path, chunk_size: int = 1024 * 1024) -> str:
    p = Path(path)
    h = hashlib.sha256()
    with p.open('rb') as f:
        while True:
            b = f.read(chunk_size)
            if not b:
                break
            h.update(b)
    return h.hexdigest()
