"""Decode the UTF-16LE MT5 Administrator config exports into readable UTF-8 JSON."""
import json
import pathlib

SRC = pathlib.Path("/home/user/refs/mt5-format-structure")
OUT = pathlib.Path("/home/user/decoded/mt5-format-structure")
OUT.mkdir(parents=True, exist_ok=True)

count = 0
for p in sorted(SRC.glob("*.json")):
    raw = p.read_bytes()
    text = raw.decode("utf-16-le", errors="replace").lstrip("\ufeff").strip()
    data = json.loads(text)
    (OUT / p.name).write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
    count += 1

print("decoded files:", count)

groups = json.loads((OUT / "Groups TCTrader-Live.json").read_text(encoding="utf-8"))
g = groups["Server"][0]["ConfigGroups"]
print("group count:", len(g))
print("group names:", [x.get("Group") for x in g])
keys = list(g[0].keys())
print("keys in first group:", len(keys))
print()
print("=== REAL MT5 ConfigGroup FIELD NAMES ===")
for i in range(0, len(keys), 5):
    print("  " + ", ".join(keys[i:i + 5]))
