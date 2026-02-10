"""Clean diagnostic — writes to file to avoid garbled output."""
import sys, os, io

old_stdout = sys.stdout
old_stderr = sys.stderr
sys.stdout = io.StringIO()
sys.stderr = io.StringIO()

os.chdir(os.path.dirname(os.path.abspath(__file__)))
from dive_core.engine.dive_connector import get_connector
c = get_connector()

sys.stdout = old_stdout
sys.stderr = old_stderr

d = c.get_disconnected()
lines = []
lines.append(f"DISCONNECTED: {len(d)}")
lines.append("-" * 100)
for x in d:
    lines.append(f"  {x['name']:40s} | {x['category']:15s} | {x['error'][:120]}")
lines.append("-" * 100)
lines.append(f"CONNECTED: {len(c.get_connected_names())}/105")

with open("_connector_report.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("Report written to _connector_report.txt")
