from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional


class DiskCache:
    def __init__(self, cache_dir: str) -> None:
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        return self.cache_dir / f'{key}.json'

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        p = self._path(key)
        if not p.exists():
            return None
        try:
            return json.loads(p.read_text(encoding='utf-8'))
        except Exception:
            return None

    def set(self, key: str, value: Dict[str, Any]) -> None:
        p = self._path(key)
        try:
            p.write_text(json.dumps(value, ensure_ascii=False), encoding='utf-8')
        except Exception:
            # ignore
            return
