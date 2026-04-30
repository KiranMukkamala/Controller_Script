import hashlib
from pathlib import Path
import csv
import sys

SDF_DIR = Path("inputs/sdf")
LDF_DIR = Path("inputs/ldf")
OUT_FILE = Path("outputs/checksums/current_input_checksums.csv")

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    rows = []

    if not SDF_DIR.exists() or not LDF_DIR.exists():
        print("❌ inputs/sdf or inputs/ldf missing")
        sys.exit(1)

    for p in sorted(SDF_DIR.glob("*.sdf")):
        rows.append(("SDF", p.name, sha256(p)))

    for p in sorted(LDF_DIR.glob("*.ldf")):
        rows.append(("LDF", p.name, sha256(p)))

    if not rows:
        print("❌ No SDF/LDF files found")
        sys.exit(1)

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with OUT_FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Type", "Filename", "SHA256"])
        writer.writerows(rows)

    print(f"✅ Current input checksums written to {OUT_FILE}")

if __name__ == "__main__":
    main()