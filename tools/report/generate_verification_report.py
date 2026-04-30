import csv
import socket
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone

STEPS = "inputs/macros/macro_steps.csv"
LINKS = "inputs/macros/macro_event_links.csv"

BASELINE_CHECKSUMS = Path("inputs/checksums/input_checksums.csv")
CURRENT_CHECKSUMS = Path("outputs/checksums/current_input_checksums.csv")

OUT = Path("outputs/html/sessionconf_report.html")


def load_csv(path):
    if not Path(path).exists():
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def csv_to_dict(rows):
    return {(r["Type"], r["Filename"]): r["SHA256"] for r in rows}


def main():
    hostname = socket.gethostname()
    utc_now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    local_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S (local)")

    steps = load_csv(STEPS)
    links = load_csv(LINKS)

    macro_counts = Counter(r["MacroName"] for r in steps)
    linked_macros = {l["MacroName"] for l in links}

    baseline = csv_to_dict(load_csv(BASELINE_CHECKSUMS))
    current = csv_to_dict(load_csv(CURRENT_CHECKSUMS))

    checksum_status = "MATCH" if baseline == current else "UPDATED"
    status_class = "ok" if checksum_status == "MATCH" else "fail"

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>SessionConf Report</title>
<style>
body {{ font-family: Arial, sans-serif; }}
table {{ border-collapse: collapse; }}
th, td {{ border: 1px solid #888; padding: 6px; }}
th {{ background: #f0f0f0; }}
.ok {{ color: green; font-weight: bold; }}
.fail {{ color: red; font-weight: bold; }}
</style>
</head>
<body>

<h1>SessionConf Documentation Report</h1>

<h2>Generation Metadata</h2>
<table>
<tr><th>Hostname</th><td>{hostname}</td></tr>
<tr><th>Generated (UTC)</th><td>{utc_now}</td></tr>
<tr><th>Generated (Local)</th><td>{local_now}</td></tr>
</table>

<h2>Input Checksum Status</h2>
<p>Status: <span class="{status_class}">{checksum_status}</span></p>

<h2>Macro Index</h2>
<ul>
"""

    for macro in sorted(macro_counts.keys()):
        html += f'<li><a href="macros/{macro}.html">{macro}</a></li>'

    html += """
</ul>

<h2>Macro Coverage</h2>
<table>
<tr><th>Macro</th><th>Step Count</th><th>Linked</th></tr>
"""

    for macro, count in sorted(macro_counts.items()):
        linked = "✅" if macro in linked_macros else "❌"
        cls = "ok" if linked == "✅" else "fail"
        html += f"<tr><td>{macro}</td><td>{count}</td><td class='{cls}'>{linked}</td></tr>"

    html += f"""
</table>

<h2>Summary</h2>
<ul>
<li>Total macros: <b>{len(macro_counts)}</b></li>
<li>Total steps: <b>{len(steps)}</b></li>
<li>Unlinked macros: <b>{len(set(macro_counts) - linked_macros)}</b></li>
</ul>

</body>
</html>
"""

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")

    print(f"✅ SessionConf report written to {OUT}")


if __name__ == "__main__":
    main()