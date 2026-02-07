"""Dive AI v20 unified entrypoint (Coder is the heart)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CODER = ROOT / "coder"
sys.path.insert(0, str(CODER))

def main():
    candidates = [
        CODER / "src" / "core" / "main.py",
        CODER / "core" / "main.py",
    ]
    for c in candidates:
        if c.exists():
            code = c.read_text(encoding="utf-8", errors="ignore")
            g = {"__name__": "__main__", "__file__": str(c)}
            exec(compile(code, str(c), "exec"), g, g)
            return
    raise SystemExit("Coder entrypoint not found. Run from v20/coder if needed.")

if __name__ == "__main__":
    main()
