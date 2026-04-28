from pathlib import Path
import re
import sys
import csv

try:
    import yaml
except ImportError:
    yaml = None


# -------------------------------------------------
# Binary string extraction
# -------------------------------------------------

def extract_strings(binary: bytes, min_len=4):
    pattern = rb"[ -~]{%d,}" % min_len
    return [
        s.decode("ascii", errors="ignore")
        for s in re.findall(pattern, binary)
    ]


# -------------------------------------------------
# CSV helper
# -------------------------------------------------

def read_csv(path: Path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


# -------------------------------------------------
# project.yaml loader
# -------------------------------------------------

def load_project_yaml():
    path = Path("inputs/metadata/project.yaml")
    if not path.exists():
        return None

    if yaml is None:
        print("❌ PyYAML required for project.yaml support")
        sys.exit(1)

    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    print(f"✅ Using project.yaml ({path})")
    return data


# -------------------------------------------------
# Unified file resolver
# -------------------------------------------------

def resolve_input_file(folder: Path, extensions, description, yaml_key=None):
    project = load_project_yaml()

    if project and yaml_key:
        try:
            filename = project["inputs"][yaml_key]
        except KeyError:
            print(f"❌ project.yaml missing inputs.{yaml_key}")
            sys.exit(1)

        path = folder / filename
        if not path.exists():
            print(f"❌ {description} '{filename}' not found in {folder}")
            sys.exit(1)

        print(f"✅ {description} selected via project.yaml: {filename}")
        return path

    # ---- fallback: first matching file ----
    files = []
    for ext in extensions:
        files.extend(folder.glob(f"*.{ext}"))

    if not files:
        print(f"❌ No {description} found in {folder}")
        sys.exit(1)

    files = sorted(files)
    chosen = files[0]

    if len(files) > 1:
        print(f"⚠️ Multiple {description} files found, using {chosen.name}")

    return chosen