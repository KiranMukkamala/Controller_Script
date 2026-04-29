import csv
import socket
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone

STEPS = "inputs/macros/macro_steps.csv"
LINKS = "inputs/macros/macro_event_links.csv"
CHECKSUMS = "outputs/checksums/input_checksums.csv"
OUT = Path("outputs/html/verification_report.html")


def load_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main():
    hostname = socket.gethostname()
    utc_now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    local_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S (local)")

    steps = load_csv(STEPS)
    links = load_csv(LINKS)

    macro_counts = Counter(r["MacroName"] for r in steps)
    linked_macros = {l["MacroName"] for l in links}

    checksums = []
    if Path(CHECKSUMS).exists():
        with open(CHECKSUMS, newline="", encoding="utf-8") as f:
            checksums = list(csv.DictReader(f))

    html = f"""<!DOCTYPE html>
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

<h2>Generation Metadata</h2>
<table>
<tr><th>Hostname</th><td>{hostname}</td></tr>
<tr><th>Generated (UTC)</th><td>{utc_now}</td></tr>
<tr><th>Generated (Local)</th><td>{local_now}</td></tr>
</table>

<h2>Input File Checksums (SHA‑256)</h2>
<table>
<tr><th>Type</th><th>Filename</th><th>SHA‑256</th></tr>
"""

    for c in checksums:
        html += (
            f"<tr><td>{c['Type']}</td>"
            f"<td>{c['Filename']}</td>"
            f"<td><code>{c['SHA256']}</code></td></tr>"
        )

    html += """
</table>

<h2>Macro Coverage</h2>
<table>
<tr><th>Macro</th><th>Step Count</th><th>Linked</th></tr>
"""

    for macro, count in sorted(macro_counts.items()):
        linked = "✅" if macro in linked_macros else "❌"
        cls = "ok" if linked == "✅" else "fail"
        html += (
            f"<tr><td>{macro}</td>"
            f"<td>{count}</td>"
            f"<td class='{cls}'>{linked}</td></tr>"
        )

    html += f"""
</table>

<h2>Summary</h2>
<ul>
<li>Total macros documented: <b>{len(macro_counts)}</b></li>
<li>Total macro steps: <b>{len(steps)}</b></li>
<li>Unlinked macros: <b>{len(set(macro_counts) - linked_macros)}</b></li>
</ul>

</body>
</html>
"""

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")

    print(f"✅ Verification report written to {OUT}")


if __name__ == "__main__":
    main()