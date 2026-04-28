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

    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    MACRO_DIR.mkdir(parents=True, exist_ok=True)

    generated = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # -------- Generate one HTML page per macro --------
    for macro, rows in steps_by_macro.items():
        rows = sorted(rows, key=lambda r: int(r["StepNumber"]) if r["StepNumber"].isdigit() else 9999)

        html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>{macro}</title>
<style>
body {{ font-family: Arial; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #999; padding: 6px; }}
th {{ background: #f0f0f0; }}
.label {{ color: #006; font-weight: bold; }}
.disabled {{ color: #999; font-style: italic; }}
</style>
</head>
<body>

<h1>{macro}</h1>
<p><b>Generated:</b> {now}</p>

<h2>Trigger(s)</h2>
<ul>
"""
        for trig in trigger_map.get(macro, ["(not externally triggered)"]):
            html += f"<li>{trig}</li>\n"

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
            step = r["StepNumber"]
            row_class = "disabled" if r["Command"].startswith("Disabled") else ""
            html += f"""
<tr id="step-{step}" class="{row_class}">
<td>{step}</td>
<td class="label">{r['Label']}</td>
<td>{r['Condition']}</td>
<td>{r['Command']}</td>
<td>{r['Value']}</td>
<td>{r['DelayMs']}</td>
<td>{r['Comment']}</td>
</tr>
"""

        html += """
</table>

<p><a href="../index.html">← Back to index</a></p>
</body>
</html>
"""

        out_file = MACRO_DIR / f"{macro}.html"
        out_file.write_text(html, encoding="utf-8")
        generated.append(macro)

    # -------- Generate index.html --------
    index = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>SessionConf Macro Index</title>
<style>
body {{ font-family: Arial; }}
</style>
</head>
<body>

<h1>SessionConf Macro Documentation</h1>
<p><b>Generated:</b> {now}</p>

<ul>
"""

    for macro in sorted(generated):
        index += f'<li><a href="macros/{macro}.html">{macro}</a></li>\n'

    index += """
</ul>

</body>
</html>
"""

    (OUT_ROOT / "index.html").write_text(index, encoding="utf-8")

    print(f"✅ Generated {len(generated)} macro HTML pages")

if __name__ == "__main__":
    main()
