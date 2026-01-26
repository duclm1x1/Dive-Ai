from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple


_GITHUB_RE = re.compile(r"https?://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+")
_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9_\-]{2,}")


PRIMARY_ORDER = [
    "n8n",
    "nextjs",
    "react",
    "nestjs",
    "tailwind",
    "security",
    "testing",
    "docs",
    "ci",
    "devtools",
    "spec",
    "ux_ui",
    "skills_registry",
    "agent_runtime",
]


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="ignore")


def _infer_kind(filename: str, text: str) -> str:
    fn = filename.lower()
    t = text.lower()
    if "awesome" in fn or "awesome" in t or "catalog" in t or "curated" in t:
        return "registry"
    if "cli" in fn or " npx " in f" {t} " or "cli" in t:
        return "cli"
    if "config" in fn or "config" in t:
        return "config"
    if "engine" in fn or "engine" in t or "runtime" in t:
        return "engine"
    if "testing" in t or "playwright" in t:
        return "testing"
    if "semgrep" in t or "trailofbits" in t or "owasp" in t or "cwe" in t:
        return "security"
    return "skillpack"


def _primary(tags: List[str]) -> str:
    for t in PRIMARY_ORDER:
        if t in tags:
            return t
    return "misc"


def _infer_stack_from_urls_and_name(skill_id: str, urls: List[str]) -> List[str]:
    s = set()
    hay = " ".join([skill_id] + urls).lower()
    if "n8n" in hay:
        s.add("n8n")
    if "next" in hay or "vercel" in hay:
        s.add("nextjs")
        s.add("react")
    if "react" in hay:
        s.add("react")
    if "nest" in hay or "nestjs" in hay:
        s.add("nestjs")
    if "tailwind" in hay:
        s.add("tailwind")
    return sorted(s)


def _infer_tags(skill_id: str, text: str, urls: List[str]) -> List[str]:
    t = text.lower()
    tags = set(["agent_runtime"])

    stacks = _infer_stack_from_urls_and_name(skill_id, urls)
    tags |= set(stacks)

    if "semgrep" in t or "trailofbits" in t or "owasp" in t or "cwe" in t:
        tags.add("security")
    if "jest" in t or "playwright" in t or "unit test" in t or "e2e" in t:
        tags.add("testing")
    if "sarif" in t or "reviewdog" in t or "github actions" in t:
        tags.add("ci")
    if "documentation" in t or "readme" in t or "openapi" in t or "swagger" in t:
        tags.add("docs")
    if "figma" in t or "a11y" in t or "accessibility" in t:
        tags.add("ux_ui")
    if "spec" in t or "acceptance criteria" in t or "prd" in t:
        tags.add("spec")
    if "cli" in t or "npx" in t or "install" in t and "skill" in t:
        tags.add("devtools")
    if "awesome" in skill_id.lower() or "awesome" in t:
        tags.add("skills_registry")

    return sorted(tags)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()


def generate(repo_root: str) -> Tuple[Dict[str, Any], str]:
    """
    Generates (automap_json, audit_md).
    """
    root = Path(repo_root)
    skills_dir = root / ".agent" / "skills"
    external_dir = root / ".agent" / "skills_external"

    skill_files: List[Path] = []
    if skills_dir.exists():
        skill_files += sorted(skills_dir.rglob("*.md"))
    if external_dir.exists():
        skill_files += sorted(external_dir.rglob("*.md"))

    skills: List[Dict[str, Any]] = []
    by_repo: Dict[str, List[str]] = defaultdict(list)
    by_kind: Dict[str, List[str]] = defaultdict(list)

    for p in skill_files:
        rel_path = f".agent/{p.relative_to(root / '.agent')}".replace("\\", "/")
        text = _read(p)
        skill_id = p.stem
        urls = _GITHUB_RE.findall(text)
        repo = urls[0].rstrip("/") if urls else ""
        kind = _infer_kind(p.name, text)
        tags = _infer_tags(skill_id, text, urls)
        primary = _primary(tags)
        base_score = 20
        if skill_id.startswith("vibe-"):
            base_score = 80
        if skill_id in {"vibe-super-coder-skills", "vibe-qa-debugging", "vibe-documentation-auto", "vibe-rlm-knowledge-lifecycle"}:
            base_score = 100

        triggers: List[str] = []
        for st in _infer_stack_from_urls_and_name(skill_id, urls):
            triggers.append(f"stack:{st}")
        for tg in tags:
            if tg in {"security", "testing", "docs", "ci", "devtools", "spec", "ux_ui", "skills_registry"}:
                triggers.append(f"category:{tg}")
        triggers.append(f"kind:{kind}")
        if base_score >= 100:
            triggers.append("need:base")
        if skill_id == "vibe-rlm-knowledge-lifecycle":
            triggers += ["need:rlm", "need:knowledge"]
        if kind == "registry":
            triggers.append("need:discovery")

        group_id = repo or skill_id

        skills.append(
            {
                "skill_id": skill_id,
                "rel_path": rel_path,
                "repo": repo,
                "kind": kind,
                "primary": primary,
                "tags": tags,
                "group_id": group_id,
                "base_score": base_score,
                "triggers": sorted(set(triggers)),
                "content_sha256": _sha256_text(text),
            }
        )
        if repo:
            by_repo[repo].append(skill_id)
        by_kind[kind].append(skill_id)

    automap = {"version": "auto", "generated_at": datetime.utcnow().isoformat() + "Z", "skills": skills}

    # Audit markdown
    lines: List[str] = []
    lines.append("# Skills Audit\n\n")
    lines.append(f"_Generated: {automap['generated_at']}_\n\n")
    lines.append(f"- Total skills indexed: **{len(skills)}**\n")
    lines.append("- Kinds: " + ", ".join(f"**{k}**({len(v)})" for k, v in sorted(by_kind.items())) + "\n\n")

    dup_repos = {r: ids for r, ids in by_repo.items() if len(ids) > 1}
    if dup_repos:
        lines.append("## Duplicate sources (same repo referenced multiple times)\n\n")
        for r, ids in sorted(dup_repos.items(), key=lambda x: -len(x[1])):
            lines.append(f"- {r}: {', '.join(ids)}\n")
        lines.append("\n")
    else:
        lines.append("## Duplicate sources\n\n- None detected by repo URL.\n\n")

    if len(by_kind.get("registry", [])) > 1:
        lines.append("## Noise control\n\n")
        lines.append(
            f"- Multiple registry skills detected (**{len(by_kind['registry'])}**). Router will auto-select **at most 1**, "
            "and only when `need:discovery` triggers.\n\n"
        )

    lines.append("## Skills index\n\n")
    lines.append("| skill_id | kind | triggers | repo |\n|---|---|---|---|\n")
    for s in sorted(skills, key=lambda x: (x["kind"], x["skill_id"])):
        trig = ", ".join([t for t in s["triggers"] if t.startswith(("stack:", "category:", "need:", "kind:"))][:6])
        if len(s["triggers"]) > 6:
            trig += "…"
        lines.append(f"| {s['skill_id']} | {s['kind']} | {trig} | {s['repo']} |\n")

    # Rule-skill mapping (rule-level routing)
    rulemap: Dict[str, List[str]] = {}
    try:
        builtin = root / '.shared' / 'vibe-coder-v13' / 'rules' / 'custom' / 'builtin_rules.json'
        if builtin.exists():
            rules_obj = json.loads(builtin.read_text(encoding='utf-8'))
            rules_list = None
            if isinstance(rules_obj, dict):
                rules_list = rules_obj.get('rules')
            elif isinstance(rules_obj, list):
                rules_list = rules_obj
            if isinstance(rules_list, list):
                # map by category -> skills
                by_cat: Dict[str, List[str]] = defaultdict(list)
                for s in skills:
                    for tg in s.get('tags') or []:
                        if isinstance(tg, str):
                            by_cat[tg].append(s['skill_id'])
                for r in rules_list:
                    if not isinstance(r, dict):
                        continue
                    rid = str(r.get('id') or '').strip()
                    cat = str(r.get('category') or '').strip().lower()
                    if not rid:
                        continue
                    picks = []
                    # prefer direct category match then modern-web / base skill fallback
                    if cat and cat in by_cat:
                        picks = by_cat[cat][:3]
                    else:
                        picks = [x for x in ['vibe-super-coder-skills','vibe-qa-debugging'] if x]
                    if picks:
                        rulemap[rid] = picks
                # wildcard conveniences
                rulemap.setdefault('N8N.*', ['vibe-tech-stack-modern-web', 'vibe-rlm-knowledge-lifecycle'])
                rulemap.setdefault('REACT.*', ['vibe-tech-stack-modern-web', 'vibe-super-coder-skills'])
                rulemap.setdefault('NEXTJS.*', ['vibe-tech-stack-modern-web', 'vibe-super-coder-skills'])
    except Exception:
        rulemap = {}
    # write to core alongside automap
    try:
        (root / '.shared' / 'vibe-coder-v13' / 'core' / 'rule_skill_map.json').write_text(
            json.dumps(rulemap, ensure_ascii=False, indent=2), encoding='utf-8')
    except Exception:
        pass

    return automap, "".join(lines)


def write(repo_root: str) -> Dict[str, str]:
    root = Path(repo_root)
    automap, audit = generate(repo_root)

    # Write automap next to router (stable import)
    core_dir = root / ".shared" / "vibe-coder-v13" / "core"
    core_dir.mkdir(parents=True, exist_ok=True)
    (core_dir / "skill_automap.json").write_text(json.dumps(automap, indent=2, ensure_ascii=False), encoding="utf-8")

    # Write audit report
    docs_dir = root / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    (docs_dir / "SKILLS_AUDIT.md").write_text(audit, encoding="utf-8")

    return {
        "automap": str((core_dir / "skill_automap.json").resolve()),
        "audit": str((docs_dir / "SKILLS_AUDIT.md").resolve()),
    }