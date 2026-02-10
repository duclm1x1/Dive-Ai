import json, os

# Check manifest
try:
    with open("skill_manifest.json", "r", encoding="utf-8") as f:
        d = json.load(f)
    print(f"Total skills in manifest: {d['total']}")
    print(f"Categories: {d['categories']}")
    if d['skills']:
        print(f"\nFirst 5 URLs:")
        for s in d['skills'][:5]:
            print(f"  {s['name']}: {s['raw_url']}")
    else:
        print("NO SKILLS IN MANIFEST!")
except FileNotFoundError:
    print("skill_manifest.json NOT FOUND")

# Check skills_library folder
lib = "skills_library"
if os.path.exists(lib):
    count = 0
    total_size = 0
    for root, dirs, files in os.walk(lib):
        for f in files:
            fp = os.path.join(root, f)
            count += 1
            total_size += os.path.getsize(fp)
    cat_dirs = [d for d in os.listdir(lib) if os.path.isdir(os.path.join(lib, d))]
    print(f"\nskills_library: {count} files, {len(cat_dirs)} category dirs")
    print(f"Total size: {total_size/1024:.1f} KB")
    if cat_dirs:
        print(f"Categories: {cat_dirs[:10]}")
else:
    print("\nskills_library folder does NOT exist")

# Check download_failures.json
if os.path.exists("download_failures.json"):
    with open("download_failures.json", "r") as f:
        fails = json.load(f)
    print(f"\nFailures: {len(fails)}")
    for ff in fails[:5]:
        print(f"  {ff}")
