"""
Dive AI — Fetch ALL 2,999 curated OpenClaw skills.
Uses Dive AI's existing AgentSkillsStandard + AutoAlgorithmCreator.

README structure: <details><summary><h3>Category</h3></summary> ... skill links ... </details>
"""
import re, os, json, time, sys
import urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SKILLS_DIR = os.path.join(BASE_DIR, "skills_library")
README_URL = "https://raw.githubusercontent.com/VoltAgent/awesome-openclaw-skills/main/README.md"
MAX_WORKERS = 8
RETRY_COUNT = 3
REQUEST_DELAY = 0.05

def slugify(name):
    return re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_')

# ══════════════════════════════════════════════════════════
# PHASE 1: Parse README
# ══════════════════════════════════════════════════════════
def phase1_parse():
    print("=" * 65)
    print("  PHASE 1: Parse README — extract skills with categories")
    print("=" * 65)
    
    with urllib.request.urlopen(README_URL) as resp:
        content = resp.read().decode("utf-8")
    print(f"  Downloaded: {len(content):,} bytes")
    
    lines = content.split("\n")
    current_cat = None
    skills = []
    seen = set()
    
    for line in lines:
        stripped = line.strip()
        
        # Detect category: <summary><h3 style="display:inline">Category Name</h3></summary>
        cat_match = re.search(r'<h3[^>]*>([^<]+)</h3>', stripped)
        if cat_match:
            current_cat = cat_match.group(1).strip()
            continue
        
        # Detect </details> = end of category
        if stripped == "</details>":
            current_cat = None
            continue
        
        # Detect skill link: - [name](url) - description
        if current_cat and stripped.startswith("- ["):
            m = re.match(r'^-\s+\[([^\]]+)\]\(([^)]+)\)\s*-?\s*(.*)', stripped)
            if m:
                name = m.group(1).strip()
                url = m.group(2).strip()
                desc = m.group(3).strip()[:200]
                
                # Convert to raw URL for SKILL.md
                raw_url = url.replace(
                    "github.com/openclaw/skills/tree/main/",
                    "raw.githubusercontent.com/openclaw/skills/main/"
                )
                if not raw_url.endswith("SKILL.md"):
                    raw_url = raw_url.rstrip("/") + "/SKILL.md"
                
                key = name.lower()
                if key not in seen:
                    seen.add(key)
                    skills.append({
                        "name": name,
                        "category": current_cat,
                        "slug": slugify(current_cat),
                        "description": desc,
                        "github_url": url,
                        "raw_url": raw_url,
                    })
    
    # Stats
    cats = defaultdict(int)
    for s in skills:
        cats[s["category"]] += 1
    
    print(f"\n  Total skills: {len(skills)}")
    print(f"  Categories:   {len(cats)}")
    for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
        print(f"    {cat:45s} {count:4d}")
    
    # Save manifest
    manifest = {
        "total": len(skills),
        "categories": len(cats),
        "category_counts": dict(sorted(cats.items(), key=lambda x: -x[1])),
        "skills": skills,
    }
    manifest_path = os.path.join(BASE_DIR, "skill_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"\n  Saved: skill_manifest.json ({os.path.getsize(manifest_path)/1024:.1f} KB)")
    
    return skills

# ══════════════════════════════════════════════════════════
# PHASE 2: Download all SKILL.md files
# ══════════════════════════════════════════════════════════
def download_one(skill):
    cat_dir = os.path.join(SKILLS_DIR, skill["slug"])
    skill_dir = os.path.join(cat_dir, skill["name"])
    skill_file = os.path.join(skill_dir, "SKILL.md")
    
    if os.path.exists(skill_file) and os.path.getsize(skill_file) > 10:
        return {"status": "cached", "name": skill["name"], "size": os.path.getsize(skill_file)}
    
    os.makedirs(skill_dir, exist_ok=True)
    
    for attempt in range(RETRY_COUNT):
        try:
            time.sleep(REQUEST_DELAY)
            req = urllib.request.Request(
                skill["raw_url"],
                headers={"User-Agent": "DiveAI-SkillFetcher/1.0"}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = resp.read()
            
            with open(skill_file, "wb") as f:
                f.write(data)
            return {"status": "ok", "name": skill["name"], "size": len(data)}
        
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return {"status": "not_found", "name": skill["name"]}
            if e.code == 403:
                print(f"\n  ⚠ Rate limited, waiting 60s...")
                time.sleep(60)
            else:
                time.sleep(RETRY_DELAY * (attempt + 1))
        except Exception:
            time.sleep(RETRY_DELAY * (attempt + 1))
    
    return {"status": "failed", "name": skill["name"]}

RETRY_DELAY = 2

def phase2_download(skills):
    print("\n" + "=" * 65)
    print("  PHASE 2: Download all SKILL.md files")
    print("=" * 65)
    
    os.makedirs(SKILLS_DIR, exist_ok=True)
    total = len(skills)
    counts = {"ok": 0, "cached": 0, "not_found": 0, "failed": 0}
    total_bytes = 0
    failures = []
    start = time.time()
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(download_one, s): s for s in skills}
        done = 0
        for future in as_completed(futures):
            done += 1
            r = future.result()
            counts[r["status"]] += 1
            total_bytes += r.get("size", 0)
            if r["status"] in ("failed", "not_found"):
                failures.append(r)
            if done % 100 == 0 or done == total:
                elapsed = time.time() - start
                rate = done / elapsed if elapsed > 0 else 0
                eta = (total - done) / rate if rate > 0 else 0
                print(f"  [{done:4d}/{total}] ok={counts['ok']} cached={counts['cached']} "
                      f"404={counts['not_found']} fail={counts['failed']} "
                      f"({total_bytes/1024/1024:.1f}MB) ETA:{eta:.0f}s")
    
    elapsed = time.time() - start
    if failures:
        with open(os.path.join(BASE_DIR, "download_failures.json"), "w") as f:
            json.dump(failures, f, indent=2)
    
    print(f"\n  Done in {elapsed:.1f}s")
    print(f"  Downloaded: {counts['ok']}")
    print(f"  Cached:     {counts['cached']}")
    print(f"  Not found:  {counts['not_found']}")
    print(f"  Failed:     {counts['failed']}")
    print(f"  Total size: {total_bytes/1024/1024:.2f} MB")
    
    return counts, total_bytes

# ══════════════════════════════════════════════════════════
# PHASE 3: Analyze using Dive AI's AgentSkillsStandard
# ══════════════════════════════════════════════════════════
def phase3_analyze(skills):
    print("\n" + "=" * 65)
    print("  PHASE 3: Analyze via Dive AI AgentSkillsStandard")
    print("=" * 65)
    
    # Import Dive AI systems
    sys.path.insert(0, os.path.join(BASE_DIR, "desktop-app", "backend"))
    try:
        from dive_core.skills.agent_skills_standard import AgentSkillsStandard
        standard = AgentSkillsStandard()
        has_standard = True
        print("  ✓ AgentSkillsStandard loaded")
    except Exception as e:
        print(f"  ⚠ AgentSkillsStandard import failed: {e}")
        has_standard = False
    
    analyses = []
    cat_stats = defaultdict(lambda: {"compatible": 0, "adaptable": 0, "incompatible": 0, "total": 0})
    platform_counts = defaultdict(int)
    parse_success = 0
    parse_fail = 0
    
    for i, skill in enumerate(skills):
        skill_file = os.path.join(SKILLS_DIR, skill["slug"], skill["name"], "SKILL.md")
        if not os.path.exists(skill_file):
            continue
        
        try:
            with open(skill_file, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except:
            continue
        
        content_lower = content.lower()
        
        # Use Dive AI parser if available
        parsed_skill = None
        if has_standard:
            try:
                parsed_skill = standard.parse_skill_md(content)
                parse_success += 1
            except:
                parse_fail += 1
        
        # Platform detection
        macos_only = any(kw in content_lower for kw in ["macos only", "osascript", "open -a", "swift", "xcode"])
        windows_ok = any(kw in content_lower for kw in ["windows", "powershell", "cross-platform"])
        
        if macos_only and not windows_ok:
            platform = "macos"
        elif windows_ok:
            platform = "windows"
        else:
            platform = "cross-platform"
        
        # Tools detection
        tool_kws = ["browser", "shell", "bash", "api", "http", "curl", "git", "docker",
                     "npm", "pip", "file", "read", "write", "database", "sql"]
        tools = [t for t in tool_kws if t in content_lower]
        
        # Deps detection
        dep_map = {"puppeteer": "puppeteer", "playwright": "playwright", "ffmpeg": "ffmpeg",
                   "homebrew": "homebrew", "pip install": "pip", "npm install": "npm", "docker": "docker"}
        deps = list(set(d for k, d in dep_map.items() if k in content_lower))
        
        # Score
        score = 0
        score += 30 if platform != "macos" else 5
        score += 20 if tools and any(t in {"shell", "bash", "api", "http", "file"} for t in tools) else 15
        score += 15 if len(content.split("\n")) > 5 else 5
        score += 15 if "homebrew" not in deps else 0
        score += 10 if "```" in content else 0
        score += 10 if len(deps) <= 2 else 5
        score = min(score, 100)
        
        if score >= 70: status = "compatible"
        elif score >= 40: status = "adaptable"
        else: status = "incompatible"
        
        analysis = {
            "name": skill["name"],
            "category": skill["category"],
            "description": skill["description"],
            "score": score,
            "status": status,
            "platform": platform,
            "tools": tools[:10],
            "dependencies": deps,
            "content_length": len(content),
            "line_count": len(content.split("\n")),
        }
        
        if parsed_skill:
            analysis["dive_parsed"] = True
            analysis["dive_name"] = getattr(parsed_skill, "name", "")
            analysis["dive_version"] = getattr(parsed_skill, "version", "")
            analysis["dive_tags"] = getattr(parsed_skill, "tags", [])[:10]
        
        analyses.append(analysis)
        cat_stats[skill["category"]][status] += 1
        cat_stats[skill["category"]]["total"] += 1
        platform_counts[platform] += 1
        
        if (i + 1) % 500 == 0:
            print(f"  Analyzed {i+1}/{len(skills)}...")
    
    total_compat = sum(1 for a in analyses if a["status"] == "compatible")
    total_adapt = sum(1 for a in analyses if a["status"] == "adaptable")
    total_incompat = sum(1 for a in analyses if a["status"] == "incompatible")
    
    print(f"\n  Analyzed:       {len(analyses)} skills")
    print(f"  🟢 Compatible:  {total_compat} ({100*total_compat/max(len(analyses),1):.1f}%)")
    print(f"  🟡 Adaptable:   {total_adapt} ({100*total_adapt/max(len(analyses),1):.1f}%)")
    print(f"  🔴 Incompatible:{total_incompat} ({100*total_incompat/max(len(analyses),1):.1f}%)")
    if has_standard:
        print(f"  Dive AI parsed: {parse_success} success, {parse_fail} fail")
    print(f"\n  Platform distribution:")
    for p, c in sorted(platform_counts.items(), key=lambda x: -x[1]):
        print(f"    {p:20s} {c:4d}")
    print(f"\n  Categories:")
    for cat, stats in sorted(cat_stats.items(), key=lambda x: -x[1]["total"]):
        print(f"    {cat:45s} 🟢{stats['compatible']:3d} 🟡{stats['adaptable']:3d} 🔴{stats['incompatible']:3d}")
    
    # Save analysis
    output = {
        "total_analyzed": len(analyses),
        "compatible": total_compat,
        "adaptable": total_adapt,
        "incompatible": total_incompat,
        "dive_ai_parse_success": parse_success,
        "dive_ai_parse_fail": parse_fail,
        "platforms": dict(platform_counts),
        "categories": {c: dict(s) for c, s in cat_stats.items()},
        "skills": sorted(analyses, key=lambda x: -x["score"]),
    }
    analysis_path = os.path.join(SKILLS_DIR, "dive_ai_analysis.json")
    with open(analysis_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\n  Saved: dive_ai_analysis.json ({os.path.getsize(analysis_path)/1024:.1f} KB)")
    
    return analyses

# ══════════════════════════════════════════════════════════
# PHASE 4: Generate registry + algorithms via AutoAlgorithmCreator
# ══════════════════════════════════════════════════════════
def phase4_registry(analyses):
    print("\n" + "=" * 65)
    print("  PHASE 4: Generate registry + auto-create algorithms")
    print("=" * 65)
    
    # Group by category
    cat_skills = defaultdict(list)
    for a in analyses:
        cat_skills[a["category"]].append({
            "name": a["name"],
            "score": a["score"],
            "status": a["status"],
            "platform": a["platform"],
            "description": a.get("description", ""),
        })
    
    # Generate Python registry
    registry_path = os.path.join(
        BASE_DIR, "desktop-app", "backend", "dive_core", "skills", "skill_registry_full.py"
    )
    os.makedirs(os.path.dirname(registry_path), exist_ok=True)
    
    lines = [
        '"""',
        f'Dive AI Complete Skill Registry — {len(analyses)} skills across {len(cat_skills)} categories.',
        'Auto-generated from awesome-openclaw-skills.',
        '"""',
        '',
        f'TOTAL_SKILLS = {len(analyses)}',
        f'TOTAL_CATEGORIES = {len(cat_skills)}',
        '',
        'SKILL_REGISTRY = {',
    ]
    
    for cat in sorted(cat_skills.keys()):
        ss = sorted(cat_skills[cat], key=lambda x: -x["score"])
        lines.append(f'    "{cat}": [')
        for s in ss:
            desc = s["description"].replace('"', '\\"')[:80]
            lines.append(f'        {{"name": "{s["name"]}", "score": {s["score"]}, '
                        f'"status": "{s["status"]}", "platform": "{s["platform"]}", '
                        f'"desc": "{desc}"}},')
        lines.append(f'    ],  # {len(ss)} skills')
    
    lines.append('}')
    lines.append('')
    lines.append('')
    lines.append('def get_compatible(category=None, min_score=70):')
    lines.append('    """Get compatible skills, optionally by category."""')
    lines.append('    results = []')
    lines.append('    for cat, skills in SKILL_REGISTRY.items():')
    lines.append('        if category and cat != category:')
    lines.append('            continue')
    lines.append('        results.extend([s for s in skills if s["score"] >= min_score])')
    lines.append('    return results')
    lines.append('')
    lines.append('')
    lines.append('def search(query, min_score=0):')
    lines.append('    """Search skills by name."""')
    lines.append('    q = query.lower()')
    lines.append('    results = []')
    lines.append('    for cat, skills in SKILL_REGISTRY.items():')
    lines.append('        for s in skills:')
    lines.append('            if q in s["name"].lower() and s["score"] >= min_score:')
    lines.append('                results.append({**s, "category": cat})')
    lines.append('    return sorted(results, key=lambda x: -x["score"])')
    lines.append('')
    
    with open(registry_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  Generated: skill_registry_full.py ({os.path.getsize(registry_path)/1024:.1f} KB)")
    
    # Try auto-algorithm creation via Dive AI
    sys.path.insert(0, os.path.join(BASE_DIR, "desktop-app", "backend"))
    try:
        from dive_core.auto_algorithm_creator import AutoAlgorithmCreator, AlgorithmBlueprint
        creator = AutoAlgorithmCreator()
        
        # Create one algorithm per category
        created = 0
        for cat, cat_skills_list in cat_skills.items():
            compat = [s for s in cat_skills_list if s["status"] == "compatible"]
            blueprint = AlgorithmBlueprint(
                name=f"openclaw_{slugify(cat)}",
                description=f"Auto-algorithm for {cat} ({len(compat)} compatible skills from OpenClaw)",
                category=slugify(cat),
                input_schema={"task": {"type": "string", "required": True}},
                output_schema={"result": {"type": "string"}, "skills_used": {"type": "list"}},
                logic_type="transform",
                tags=[slugify(cat), "openclaw", "auto-generated"],
            )
            try:
                result = creator.create(blueprint)
                if result.get("status") == "success" or result.get("created"):
                    created += 1
            except Exception as e:
                pass  # Some may fail, that's OK
        
        print(f"  AutoAlgorithmCreator: {created}/{len(cat_skills)} category algorithms created")
        stats = creator.get_stats()
        print(f"  Creator stats: {json.dumps(stats, indent=2)}")
    except Exception as e:
        print(f"  ⚠ AutoAlgorithmCreator: {e}")
    
    return registry_path

# ══════════════════════════════════════════════════════════
# PHASE 5: Final report
# ══════════════════════════════════════════════════════════
def phase5_report():
    print("\n" + "=" * 65)
    print("  FINAL REPORT")
    print("=" * 65)
    
    file_count = 0
    total_size = 0
    for root, dirs, files in os.walk(SKILLS_DIR):
        for f in files:
            if f == "SKILL.md":
                file_count += 1
                total_size += os.path.getsize(os.path.join(root, f))
    
    cat_dirs = [d for d in os.listdir(SKILLS_DIR)
                if os.path.isdir(os.path.join(SKILLS_DIR, d))]
    
    print(f"  SKILL.md files:    {file_count}")
    print(f"  Category folders:  {len(cat_dirs)}")
    print(f"  Total disk usage:  {total_size/1024/1024:.2f} MB")
    
    # Check analysis
    analysis_path = os.path.join(SKILLS_DIR, "dive_ai_analysis.json")
    if os.path.exists(analysis_path):
        with open(analysis_path, "r") as f:
            d = json.load(f)
        print(f"  Skills analyzed:   {d['total_analyzed']}")
        print(f"  Compatible:        {d['compatible']}")
        print(f"  Adaptable:         {d['adaptable']}")
        print(f"  Incompatible:      {d['incompatible']}")
        print(f"  Dive AI parsed:    {d.get('dive_ai_parse_success', 'N/A')}")
    
    print("=" * 65)

# ══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print()
    print("╔════════════════════════════════════════════════════════════╗")
    print("║  DIVE AI — FULL SKILL FETCH & INTEGRATION                ║")
    print("║  Using existing AgentSkillsStandard + AutoAlgorithmCreator║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    skills = phase1_parse()
    
    if len(skills) == 0:
        print("\n  ERROR: No skills parsed! Check README format.")
        sys.exit(1)
    
    counts, total_bytes = phase2_download(skills)
    analyses = phase3_analyze(skills)
    registry_path = phase4_registry(analyses)
    phase5_report()
