"""Quick debug to see README structure around skill sections."""
import urllib.request, re

url = "https://raw.githubusercontent.com/VoltAgent/awesome-openclaw-skills/main/README.md"
with urllib.request.urlopen(url) as resp:
    content = resp.read().decode("utf-8")

lines = content.split("\n")
print(f"Total lines: {len(lines)}")

# Show lines 100-130 (after TOC, start of skills)
print("\n=== LINES 100-140 ===")
for i in range(99, min(140, len(lines))):
    print(f"{i+1:4d} | {lines[i][:150]}")

# Find all ## and ### headers
print("\n=== ALL H2 HEADERS ===")
for i, line in enumerate(lines):
    if re.match(r'^## ', line.strip()):
        print(f"{i+1:4d} | {line.strip()[:120]}")

# Show transition between categories (look for non-link lines between skills)
print("\n=== NON-LINK LINES BETWEEN 110-3300 ===")
in_skills = False
for i in range(109, min(3300, len(lines))):
    stripped = lines[i].strip()
    if stripped.startswith("- ["):
        in_skills = True
        continue
    if in_skills and stripped and not stripped.startswith("- ["):
        print(f"{i+1:4d} | {stripped[:150]}")
