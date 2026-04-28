import sys
from pathlib import Path

# --- FIX ---
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from tools.utils.common import read_csv, resolve_input_file

def main():
    macros = read_csv(Path("outputs/macros.csv"))

    events_csv = resolve_input_file(
        Path("inputs/events"), ["csv"], "Events CSV", yaml_key="events"
    )
    gui_csv = resolve_input_file(
        Path("inputs/gui"), ["csv"], "GUI CSV", yaml_key="gui"
    )

    events = read_csv(events_csv)
    gui = read_csv(gui_csv)

    out = Path("outputs/html/sessionconf_report.html")
    out.parent.mkdir(parents=True, exist_ok=True)

    html = """<!DOCTYPE html>
<html><head>
<meta charset="UTF-8">
<title>SessionConf Report</title>
<style>
body{font-family:Arial;margin:20px}
table{border-collapse:collapse;width:100%}
th,td{border:1px solid #ccc;padding:6px}
th{background:#f0f0f0}
</style></head><body>
<h1>SessionConf Configuration Report</h1>
"""

    html += "<h2>Macros</h2><table>"
    html += "<tr><th>Name</th><th>Autostart</th><th>Commands</th></tr>"
    for m in macros:
        html += (
            f"<tr><td>{m['Name']}</td>"
            f"<td>{m['Autostart']}</td>"
            f"<td>{m['CommandCount'] or 'N/A'}</td></tr>"
        )
    html += "</table>"

    html += "<h2>Events → Macros</h2><table>"
    html += "<tr><th>Device</th><th>Condition</th><th>Macro</th></tr>"
    for e in events:
        html += (
            f"<tr><td>{e['Device']}</td>"
            f"<td>{e['Condition']}</td>"
            f"<td>{e['Macro']}</td></tr>"
        )
    html += "</table>"

    html += "<h2>GUI Widgets → Signals</h2><table>"
    html += "<tr><th>Widget</th><th>Signal</th><th>Origin</th></tr>"
    for g in gui:
        html += (
            f"<tr><td>{g['WidgetName']}</td>"
            f"<td>{g['Signal']}</td>"
            f"<td>{g['SignalOrigin']}</td></tr>"
        )
    html += "</table></body></html>"

    out.write_text(html, encoding="utf-8")
    print("✅ HTML report generated")

if __name__ == "__main__":
    main()