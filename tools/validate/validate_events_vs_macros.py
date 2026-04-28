import sys
from pathlib import Path

# --- FIX ---
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import sys as _sys
from tools.utils.common import read_csv, resolve_input_file

EVENTS_DIR = Path("inputs/events")
MACROS_CSV = Path("outputs/macros.csv")

def main():
    events_csv = resolve_input_file(
        EVENTS_DIR, ["csv"], "Events CSV", yaml_key="events"
    )

    events = read_csv(events_csv)
    macros = read_csv(MACROS_CSV)
    known = {m["Name"] for m in macros}

    errors = False
    for e in events:
        m = e["Macro"].strip()
        if m and m not in known:
            print(f"❌ Event references unknown macro: {m}")
            errors = True

    if errors:
        _sys.exit(1)

    print("✅ Events validated")

if __name__ == "__main__":
    main()