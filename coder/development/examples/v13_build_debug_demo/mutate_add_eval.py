\
#!/usr/bin/env python3
import sys
from pathlib import Path

def main(outdir: str) -> int:
    root = Path(outdir)
    target = root / "app" / "page.tsx"
    if not target.exists():
        print("Missing", target)
        return 2
    txt = target.read_text(encoding="utf-8")
    if "eval(" in txt:
        print("Already mutated.")
        return 0
    inject = "\n// INTENTIONAL REGRESSION FOR BASELINE GATE TEST\nconst _x = eval('1+1');\n"
    # add near top of component
    out = txt.replace("export default function Page()", inject + "\nexport default function Page()", 1)
    target.write_text(out, encoding="utf-8")
    print("Injected eval() into", target)
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else "."))
