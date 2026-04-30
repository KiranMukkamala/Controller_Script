import csv
from pathlib import Path
from collections import defaultdict
from datetime import datetime

STEPS_FILE = "inputs/macros/macro_steps.csv"
LINKS_FILE = "inputs/macros/macro_event_links.csv"

OUT_ROOT = Path("outputs/html")
MACRO_DIR = OUT_ROOT / "macros"


def load_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main():
    steps = load_csv(STEPS_FILE)
    links = load_csv(LINKS_FILE)

    steps_by_macro = defaultdict(list)
    for row in steps:
        steps_by_macro[row["MacroName"]].append(row)

    trigger_map = defaultdict(list)
    for l in links:
        trigger_map[l["MacroName"]].append(
            f"{l['TriggerType']}: {l['TriggerSource']}"
        )

    MACRO_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for macro, rows in steps_by_macro.items():
        rows = sorted(
            rows,
            key=lambda r: int(r["StepNumber"])
            if r["StepNumber"].isdigit() else 9999
        )

        html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>{macro}</title>
<style>
body {{ font-family: Arial, sans-serif; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #999; padding: 6px; }}
th {{ background: #f0f0f0; }}
.disabled {{ color: #999; font-style: italic; }}
</style>
</head>
<body>

<h1>{macro}</h1>
<p><b>Generated:</b> {now}</p>

<h2>Trigger(s)</h2>
<ul>
"""

        for trig in trigger_map.get(macro, ["(Internal / no direct trigger)"]):
            html += f"<li>{trig}</li>"

        html += """
</ul>

<h2>Steps</h2>
<table>
<tr>
<th>#</th>
<th>Label</th>
<th>Condition</th>
<th>Command</th>
<th>Value</th>
<th>Delay</th>
<th>Comment</th>
</tr>
"""

        for r in rows:
            cls = "disabled" if r["Command"].startswith("Disabled") else ""
            html += f"""
<tr id="step-{r['StepNumber']}" class="{cls}">
<td>{r['StepNumber']}</td>
<td>{r['Label']}</td>
<td>{r['Condition']}</td>
<td>{r['Command']}</td>
<td>{r['Value']}</td>
<td>{r['DelayMs']}</td>
<td>{r['Comment']}</td>
</tr>
"""

        html += """
</table>

<p><a href="../sessionconf_report.html">Back to SessionConf Report</a></p>
</body>
</html>
"""

        out_file = MACRO_DIR / f"{macro}.html"
        out_file.write_text(html, encoding="utf-8")

    print(f"✅ Generated {len(steps_by_macro)} macro HTML pages")


if __name__ == "__main__":
    main()