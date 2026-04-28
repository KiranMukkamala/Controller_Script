import csv
import sys
from collections import defaultdict

STEPS_FILE = "inputs/macros/macro_steps.csv"
LINKS_FILE = "inputs/macros/macro_event_links.csv"

VALID_TRIGGER_TYPES = {"Event", "MacroCall", "Service", "Autostart"}


def load_csv(path):
    try:
        with open(path, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))
    except FileNotFoundError:
        print(f"❌ Missing required file: {path}")
        sys.exit(1)


def main():
    steps = load_csv(STEPS_FILE)
    links = load_csv(LINKS_FILE)

    print("\n=== Macro Consistency Check ===\n")

    errors = False

    # ------------------------------------------------------------------
    # Build macro → steps map
    # ------------------------------------------------------------------
    macro_steps = defaultdict(list)
    for row in steps:
        macro_steps[row["MacroName"]].append(row)

    step_macros = set(macro_steps.keys())
    link_macros = {l["MacroName"] for l in links}

    # ------------------------------------------------------------------
    # Check: macros missing in macro_event_links.csv
    # ------------------------------------------------------------------
    missing_links = step_macros - link_macros
    if missing_links:
        errors = True
        print("❌ Macros missing in macro_event_links.csv:")
        for m in sorted(missing_links):
            print(f"  - {m}")
    else:
        print("✅ All macros are linked in macro_event_links.csv")

    # ------------------------------------------------------------------
    # Check: links referencing undefined macros
    # ------------------------------------------------------------------
    orphan_links = link_macros - step_macros
    if orphan_links:
        errors = True
        print("\n❌ macro_event_links.csv references undefined macros:")
        for m in sorted(orphan_links):
            print(f"  - {m}")
    else:
        print("✅ All linked macros exist in macro_steps CSV")

    # ------------------------------------------------------------------
    # Check: valid TriggerType values
    # ------------------------------------------------------------------
    invalid_triggers = [
        l for l in links if l["TriggerType"] not in VALID_TRIGGER_TYPES
    ]
    if invalid_triggers:
        errors = True
        print("\n❌ Invalid TriggerType values:")
        for l in invalid_triggers:
            print(f"  - {l['MacroName']}: {l['TriggerType']}")
    else:
        print("✅ All TriggerType values are valid")

    # ------------------------------------------------------------------
    # Per-macro structural checks
    # ------------------------------------------------------------------
    for macro, rows in macro_steps.items():
        # ---- Step number continuity ----
        step_numbers = []
        for r in rows:
            try:
                step_numbers.append(int(r["StepNumber"]))
            except ValueError:
                pass  # labels like CodingError / Exit

        if step_numbers:
            step_numbers.sort()
            expected = list(range(step_numbers[0], step_numbers[-1] + 1))
            if step_numbers != expected:
                errors = True
                print(f"\n❌ Step number gap in macro '{macro}'")
                print(f"   Found   : {step_numbers}")
                print(f"   Expected: {expected}")

        # ---- Jump / Label integrity ----
        labels = {r["Label"] for r in rows if r["Label"]}
        jumps = {
            r["Value"]
            for r in rows
            if r["Command"].startswith("Jump") and r["Value"]
        }

        missing_labels = jumps - labels
        if missing_labels:
            errors = True
            print(f"\n❌ Macro '{macro}' jumps to missing label(s):")
            for l in missing_labels:
                print(f"   -> {l}")

    # ------------------------------------------------------------------
    # Final result
    # ------------------------------------------------------------------
    if errors:
        print("\n❌ Macro consistency check FAILED\n")
        sys.exit(1)

    print("\n✅ Macro consistency check PASSED\n")


if __name__ == "__main__":
    main()
