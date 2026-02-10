"""
Extract ALL skills from awesome-openclaw-skills and build Dive AI registry.
Fixed category parsing and generates the complete skill_registry_full.py file.
"""
import re, json, urllib.request, os

URL = "https://raw.githubusercontent.com/VoltAgent/awesome-openclaw-skills/main/README.md"

print("Downloading awesome-openclaw-skills README...")
with urllib.request.urlopen(URL) as resp:
    content = resp.read().decode("utf-8")
print(f"Downloaded {len(content)} bytes ({len(content)/1024:.1f} KB)")

lines = content.split("\n")
current_category = None
categories = {}
all_skills = []

KNOWN_CATEGORIES = [
    "Coding Agents & IDEs", "Git & GitHub", "Moltbook",
    "Web & Frontend Development", "DevOps & Cloud",
    "Browser & Automation", "Image & Video Generation",
    "Apple Apps & Services", "Search & Research",
    "Clawdbot Tools", "CLI Utilities", "Marketing & Sales",
    "Productivity & Tasks", "AI & LLMs", "Data & Analytics",
    "Finance", "Media & Streaming", "Notes & PKM",
    "PDF & Documents", "iOS & macOS Development",
    "Transportation", "Personal Development",
    "Health & Fitness", "Communication",
    "Speech & Transcription", "Smart Home & IoT",
    "Shopping & E-commerce", "Calendar & Scheduling",
    "Self-Hosted & Automation", "Security & Passwords",
    "Gaming", "Agent-to-Agent Protocols",
]

for line in lines:
    stripped = line.strip()
    
    # Detect H3 category headers
    h3_match = re.match(r'^###\s+(.+)$', stripped)
    if h3_match:
        cat_name = h3_match.group(1).strip()
        if cat_name in KNOWN_CATEGORIES:
            current_category = cat_name
            if current_category not in categories:
                categories[current_category] = []
            continue
    
    # Detect skill entries
    if current_category and stripped.startswith("- ["):
        m = re.match(r'^-\s+\[([^\]]+)\]\(([^)]+)\)\s*-?\s*(.*)', stripped)
        if m:
            name = m.group(1).strip()
            url = m.group(2).strip()
            desc = m.group(3).strip()[:120]
            
            categories[current_category].append(name)
            all_skills.append({
                "name": name,
                "category": current_category,
                "url": url,
                "description": desc,
            })

# Deduplicate
seen = set()
unique_skills = []
for s in all_skills:
    key = (s["name"].lower(), s["category"])
    if key not in seen:
        seen.add(key)
        unique_skills.append(s)

# Category stats
cat_counts = {}
for s in unique_skills:
    cat_counts[s["category"]] = cat_counts.get(s["category"], 0) + 1

print(f"\n{'='*60}")
print(f"  EXTRACTION COMPLETE")
print(f"{'='*60}")
print(f"  Total raw entries:    {len(all_skills)}")
print(f"  Unique skills:        {len(unique_skills)}")
print(f"  Categories:           {len(cat_counts)}")
print()
for cat, count in sorted(cat_counts.items(), key=lambda x: -x[1]):
    print(f"  {cat:45s} {count:4d}")

# Save full JSON
output = {
    "total_skills": len(unique_skills),
    "total_categories": len(cat_counts),
    "categories": {cat: count for cat, count in sorted(cat_counts.items(), key=lambda x: -x[1])},
    "skills": unique_skills,
}
with open("all_openclaw_skills.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

# Save names by category
cat_names = {}
for s in unique_skills:
    cat_names.setdefault(s["category"], []).append(s["name"])
with open("skill_names_by_category.json", "w", encoding="utf-8") as f:
    json.dump(cat_names, f, indent=2, ensure_ascii=False)

# Sizes
js = os.path.getsize("all_openclaw_skills.json")
cs = os.path.getsize("skill_names_by_category.json")
print(f"\n{'='*60}")
print(f"  FILE SIZES")
print(f"{'='*60}")
print(f"  Raw README:                   {len(content)/1024:.1f} KB ({len(content)/1024/1024:.2f} MB)")
print(f"  all_openclaw_skills.json:     {js/1024:.1f} KB ({js/1024/1024:.2f} MB)")
print(f"  skill_names_by_category.json: {cs/1024:.1f} KB ({cs/1024/1024:.2f} MB)")

# Estimate Python registry size
# Each skill in Python: ~60 bytes (just name string) 
py_names_only = sum(len(s["name"]) + 10 for s in unique_skills)
py_with_desc = sum(len(s["name"]) + len(s["description"]) + 30 for s in unique_skills)
print(f"\n  Python registry (names only):  {py_names_only/1024:.1f} KB ({py_names_only/1024/1024:.2f} MB)")
print(f"  Python registry (name+desc):  {py_with_desc/1024:.1f} KB ({py_with_desc/1024/1024:.2f} MB)")
print(f"{'='*60}")

# Now generate the Python registry file
print("\nGenerating skill_registry_full.py ...")

py_lines = []
py_lines.append('"""')
py_lines.append('Dive AI — Complete Skill Registry')
py_lines.append(f'Auto-extracted from awesome-openclaw-skills: {len(unique_skills)} unique skills across {len(cat_counts)} categories.')
py_lines.append(f'Source: https://github.com/VoltAgent/awesome-openclaw-skills')
py_lines.append('"""')
py_lines.append('')
py_lines.append('# Category → list of skill names')
py_lines.append('FULL_SKILL_REGISTRY = {')

for cat in sorted(cat_counts.keys()):
    skills = sorted(set(cat_names.get(cat, [])))
    py_lines.append(f'    "{cat}": [')
    # Write 5 per line
    for i in range(0, len(skills), 5):
        batch = skills[i:i+5]
        line = ", ".join(f'"{s}"' for s in batch)
        py_lines.append(f'        {line},')
    py_lines.append(f'    ],  # {len(skills)} skills')

py_lines.append('}')
py_lines.append('')
py_lines.append(f'TOTAL_SKILLS = {len(unique_skills)}')
py_lines.append(f'TOTAL_CATEGORIES = {len(cat_counts)}')
py_lines.append('')

# Write the Python file
py_content = "\n".join(py_lines)
py_path = os.path.join("desktop-app", "backend", "dive_core", "skills", "skill_registry_full.py")
os.makedirs(os.path.dirname(py_path), exist_ok=True)
with open(py_path, "w", encoding="utf-8") as f:
    f.write(py_content)

py_size = os.path.getsize(py_path)
print(f"  skill_registry_full.py:       {py_size/1024:.1f} KB ({py_size/1024/1024:.2f} MB)")
print(f"\nDone! All {len(unique_skills)} skills registered into Dive AI.")
