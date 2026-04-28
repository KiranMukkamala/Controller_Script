import csv
from pathlib import Path
import re
import sys

HTML_ROOT = Path("outputs/html")
MACROS_DIR = HTML_ROOT / "macros"
EVENT_LINKS = "inputs/macros/macro_event_links.csv"
STEPS = "inputs/macros/macro_steps.csv"

def load_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def main():
    links = load_csv(EVENT_LINKS)
    steps = load_csv(STEPS)

    macro_steps = {}
    for row in steps:
        macro_steps.setdefault(row["MacroName"], set()).add(row["StepNumber"])

    errors = False
    print("\n=== HTML Event → Macro → Step Link Check ===\n")

    for link in links:
        macro = link["MacroName"]
        macro_file = MACROS_DIR / f"{macro}.html"

        if not macro_file.exists():
            print(f"❌ Missing macro HTML page: {macro}")
            errors = True
            continue

        html = macro_file.read_text(encoding="utf-8")

        # Check that steps are anchor-linked
        for step in macro_steps.get(macro, []):
            anchor = f"step-{step}"
            if anchor not in html:
                print(f"❌ Missing step anchor in {macro}.html -> step {step}")
                errors = True

    if errors:
        print("\n❌ HTML navigation validation FAILED\n")
        sys.exit(1)

    print("✅ HTML Event → Macro → Step navigation valid\n")

if __name__ == "__main__":
    main()