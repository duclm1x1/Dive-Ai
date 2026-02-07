\
#!/usr/bin/env python3
import os, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VIBE = ROOT / ".shared" / "vibe-coder-v13" / "vibe.py"
SPEC = Path(__file__).resolve().parent / "spec.nextjs.yml"
OUTDIR = Path(__file__).resolve().parent / "out"

def run(cmd):
    print("\n$ " + " ".join(map(str, cmd)))
    p = subprocess.run(list(map(str, cmd)), text=True, capture_output=True)
    print("exit:", p.returncode)
    if p.stdout.strip():
        print("stdout:\n", p.stdout)
    if p.stderr.strip():
        print("stderr:\n", p.stderr)
    return p.returncode

def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)

    # 1) First build: baseline is missing -> baseline-init gate creates it (E3).
    rc1 = run([sys.executable, str(VIBE), "build",
               "--kind", "nextjs",
               "--spec", str(SPEC),
               "--outdir", str(OUTDIR),
               "--mode", "fast",
               "--sarif-out", str(OUTDIR / ".vibe" / "reports" / "vibe-build.sarif.json")])

    # 2) Mutate scaffold to introduce a regression (JS eval) -> baseline-compare should fail.
    mutate = Path(__file__).resolve().parent / "mutate_add_eval.py"
    rc_m = run([sys.executable, str(mutate), str(OUTDIR)])

    # 3) Second build: baseline exists -> compare gate runs. Expected: non-zero exit.
    rc2 = run([sys.executable, str(VIBE), "build",
               "--kind", "nextjs",
               "--spec", str(SPEC),
               "--outdir", str(OUTDIR),
               "--mode", "fast",
               "--sarif-out", str(OUTDIR / ".vibe" / "reports" / "vibe-build.sarif.json")])

    print("\nSummary:")
    print(" first build rc =", rc1, "(expected 0)")
    print(" mutate rc      =", rc_m, "(expected 0)")
    print(" second build rc=", rc2, "(expected non-zero due to baseline regression)")
    print("\nArtifacts:")
    print(" baseline:", OUTDIR / ".vibe" / "baseline.json")
    print(" compare :", OUTDIR / ".vibe" / "reports" / "baseline-compare.json")
    print(" evidence:", OUTDIR / ".vibe" / "reports" / "vibe-build.evidencepack.json")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
