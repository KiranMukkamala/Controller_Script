import csv
from pathlib import Path
import sys

BASELINE = Path("inputs/checksums/input_checksums.csv")
CURRENT = Path("outputs/checksums/current_input_checksums.csv")

def load_csv(path):
    with path.open(newline="", encoding="utf-8") as f:
        return {(r["Type"], r["Filename"]): r["SHA256"] for r in csv.DictReader(f)}

def main():
    if not CURRENT.exists():
        print("❌ Current checksum file missing")
        sys.exit(1)

    current = load_csv(CURRENT)

    if not BASELINE.exists():
        print("⚠️ No baseline found — creating initial baseline")
        BASELINE.parent.mkdir(parents=True, exist_ok=True)
        BASELINE.write_text(CURRENT.read_text(encoding="utf-8"), encoding="utf-8")
        print("✅ Baseline checksums created")
        return

    baseline = load_csv(BASELINE)

    diffs = []

    for key, cur_hash in current.items():
        base_hash = baseline.get(key)
        if base_hash != cur_hash:
            diffs.append((key, base_hash, cur_hash))

    if not diffs:
        print("✅ Input checksums match baseline")
        return

    print("\n⚠️ Input checksum differences detected:\n")
    for (typ, name), old, new in diffs:
        print(f"{typ} {name}")
        print(f"  OLD: {old}")
        print(f"  NEW: {new}\n")

    # Non-interactive support (CI)
    auto_accept = "--accept" in sys.argv or \
                  (os.getenv("CHECKSUM_AUTO_ACCEPT") == "1")

    if auto_accept:
        print("✅ Auto-accept enabled — updating baseline")
        BASELINE.write_text(CURRENT.read_text(encoding="utf-8"), encoding="utf-8")
        return

    choice = input("Accept new checksums and update baseline? [y/N]: ").strip().lower()
    if choice == "y":
        BASELINE.write_text(CURRENT.read_text(encoding="utf-8"), encoding="utf-8")
        print("✅ Baseline updated")
    else:
        print("❌ Checksum mismatch not accepted — aborting")
        sys.exit(1)

if __name__ == "__main__":
    import os
    main()