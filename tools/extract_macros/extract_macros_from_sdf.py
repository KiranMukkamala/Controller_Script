import sys
from pathlib import Path

# --- FIX: ensure repo root is on sys.path ---
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import csv
from tools.utils.common import extract_strings, resolve_input_file

INPUT_DIR = Path("inputs/sdf")
OUT = Path("outputs/macros.csv")

def main():
    sdf = resolve_input_file(
        INPUT_DIR, ["sdf"], "SDF file", yaml_key="sdf"
    )

    strings = extract_strings(sdf.read_bytes())
    macros = {}

    for s in strings:
        if s.startswith("macro_"):
            macros[s] = {
                "Name": s,
                "Autostart": "Yes" if s == "macro_Start_Software" else "No",
                "CommandCount": ""
            }

    for i, s in enumerate(strings):
        if s in macros:
            for w in strings[i:i+6]:
                if w.isdigit() and 0 < int(w) < 500:
                    macros[s]["CommandCount"] = w
                    break

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["Name", "Autostart", "CommandCount"]
        )
        writer.writeheader()
        writer.writerows(macros.values())

    print("✅ Macros extracted")

if __name__ == "__main__":
    main()