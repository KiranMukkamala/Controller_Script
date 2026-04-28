import csv
from pathlib import Path
from collections import Counter
from datetime import datetime

STEPS = "inputs/macros/macro_steps.csv"
LINKS = "inputs/macros/macro_event_links.csv"
OUT = Path("outputs/html/verification_report.html")

def load_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def main():
    steps = load_csv(STEPS)
    links = load_csv(LINKS)

    macro_counts = Counter(r["MacroName"] for r in steps)
    linked_macros = {l["MacroName"] for l in links}

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>SessionConf Verification Report</title>
<style>
body {{ font-family: Arial, sans-serif; }}
table {{ border-collapse: collapse; }}
th, td {{ border: 1px solid #888; padding: 6px; }}
th {{ background: #f0f0f0; }}
.ok {{ color: green; }}
.fail {{ color: red; }}
</style>
</head>
<body>

<h1>SessionConf Documentation Verification Report</h1>
<p><b>Generated:</b> {now}</p>

<h2>Macro Coverage</h2>
<table>
<tr><th>Macro</th><th>Step Count</th><th>Linked</th></tr>
"""

    for macro, count in sorted(macro_counts.items()):
        linked = "✅" if macro in linked_macros else "❌"
        cls = "ok" if linked == "✅" else "fail"
        html += f"<tr><td>{macro}</td><td>{count}</td><td class='{cls}'>{linked}</td></tr>"

    html += """
</table>

<h2>Summary</h2>
<ul>
<li>Total macros documented: <b>{}</b></li>
<li>Total macro steps: <b>{}</b></li>
<li>Unlinked macros: <b>{}</b></li>
</ul>

</body>
</html>
""".format(
        len(macro_counts),
        len(steps),
        len(set(macro_counts) - linked_macros)
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")

    print(f"✅ Verification report written to {OUT}")

if __name__ == "__main__":
    main()