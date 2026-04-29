import csv
import hashlib
from pathlib import Path
import sys

SDF_DIR = Path("inputs/sdf")
LDF_DIR = Path("inputs/ldf")
CHECKSUM_FILE = Path("outputs/checksums/input_checksums.csv")

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    if not CHECKSUM_FILE.exists():
        print("⚠️ No checksum baseline found — skipping validation")
        return

    baseline = {}
    with CHECKSUM_FILE.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            baseline[(row["Type"], row["Filename"])] = row["SHA256"]

    errors = False

    for kind, folder, pattern in [
        ("SDF", SDF_DIR, "*.sdf"),
        ("LDF", LDF_DIR, "*.ldf"),
    ]:
        for p in folder.glob(pattern):
            key = (kind, p.name)
            if key not in baseline:
                print(f"❌ New {kind} file detected: {p.name}")
                errors = True
                continue

            current = sha256(p)
            if current != baseline[key]:
                print(f"❌ {kind} file changed: {p.name}")
                print(f"   Expected: {baseline[key]}")
                print(f"   Found   : {current}")
                errors = True

    if errors:
        print("\n❌ Input checksum validation FAILED")
        sys.exit(1)

    print("✅ Input checksum validation PASSED")

if __name__ == "__main__":
    main()
