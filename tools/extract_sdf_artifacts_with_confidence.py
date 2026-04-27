import re
import sys
import csv
from pathlib import Path
from collections import defaultdict

# ---------------- Helpers ----------------

def extract_strings(blob, min_len=4):
    return [
        s.decode("ascii", errors="ignore")
        for s in re.findall(rb"[ -~]{%d,}" % min_len, blob)
    ]

def classify(strings):
    macros, events, signals = set(), set(), set()
    for s in strings:
        sl = s.lower()
        if "macro" in sl and s.isidentifier():
            macros.add(s)
        elif any(k in sl for k in ["event", "startup", "power", "ignition"]):
            events.add(s)
        elif s.isupper() and 2 < len(s) < 32:
            signals.add(s)
    return sorted(macros), sorted(events), sorted(signals)

def confidence(s, m=None, e=None, sig=None):
    if m and e and m in s and e in s:
        return "HIGH", "Same string"
    if (m and m in s) or (e and e in s):
        return "MEDIUM", "Near reference"
    if sig and sig in s:
        return "MEDIUM", "Signal proximity"
    return "LOW", "Global occurrence"


def generate_html_report(output_dir, sdf_name, macros, events, signals, links):
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>SDF Extraction Report – {sdf_name}</title>
<style>
body {{
  font-family: Arial, sans-serif;
  margin: 20px;
}}
h1, h2, h3 {{
  color: #333;
}}
table {{
  border-collapse: collapse;
  width: 100%;
  margin-bottom: 20px;
}}
th, td {{
  border: 1px solid #ccc;
  padding: 6px 8px;
  text-align: left;
}}
th {{
  background-color: #f2f2f2;
}}
.conf-HIGH {{ background-color: #d4edda; }}
.conf-MEDIUM {{ background-color: #fff3cd; }}
.conf-LOW {{ background-color: #f8d7da; }}
.small {{
  font-size: 0.9em;
  color: #555;
}}
</style>
</head>
<body>

<h1>SDF Extraction Report</h1>
<p class="small">
File: <strong>{sdf_name}</strong><br>
Generated automatically – verify LOW / MEDIUM confidence items in SessionConf.
</p>

<h2>Overview</h2>
<ul>
  <li>Macros: {len(macros)}</li>
  <li>Events: {len(events)}</li>
  <li>Signals: {len(signals)}</li>
  <li>Total links: {len(links)}</li>
</ul>

<h2>Confidence Summary</h2>
<ul>
  <li>HIGH: {sum(1 for l in links if l[3] == "HIGH")}</li>
  <li>MEDIUM: {sum(1 for l in links if l[3] == "MEDIUM")}</li>
  <li>LOW: {sum(1 for l in links if l[3] == "LOW")}</li>
</ul>

<h2>Macro – Event – Signal Links</h2>
<table>
<tr>
  <th>Macro</th>
  <th>Event</th>
  <th>Signal</th>
  <th>Confidence</th>
  <th>Context</th>
</tr>
"""

    for m, e, s, conf, ctx in links:
        html += f"""
<tr class="conf-{conf}">
  <td>{m}</td>
  <td>{e}</td>
  <td>{s}</td>
  <td>{conf}</td>
  <td class="small">{ctx}</td>
</tr>
"""

    html += """
</table>

<h2>Macros</h2>
"""
    for m in sorted(macros):
        html += f"<h3>{m}</h3><ul>"
        for lm, le, ls, conf, _ in links:
            if lm == m:
                html += f"<li>{le} → {ls} ({conf})</li>"
        html += "</ul>"

    html += """
<h2>Events</h2>
"""
    for e in sorted(events):
        html += f"<h3>{e}</h3><ul>"
        for lm, le, ls, conf, _ in links:
            if le == e:
                html += f"<li>{lm} → {ls} ({conf})</li>"
        html += "</ul>"

    html += """
<h2>Signals</h2>
"""
    for s in sorted(signals):
        html += f"<h3>{s}</h3><ul>"
        for lm, le, ls, conf, _ in links:
            if ls == s:
                html += f"<li>{lm} / {le} ({conf})</li>"
        html += "</ul>"

    html += """
</body>
</html>
"""

    report_path = output_dir / "sdf_extraction_report.html"
    report_path.write_text(html, encoding="utf-8")
    return report_path

# ---------------- Main ----------------

def main():
    if len(sys.argv) != 3:
        print("Usage: python extract.py input.sdf out_dir")
        sys.exit(1)

    sdf = Path(sys.argv[1])
    out = Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)

    macros_dir = out / "macros"
    events_dir = out / "events"
    signals_dir = out / "signals"
    for d in (macros_dir, events_dir, signals_dir):
        d.mkdir(parents=True, exist_ok=True)

    strings = extract_strings(sdf.read_bytes())
    macros, events, signals = classify(strings)

    links = []

    for s in strings:
        for m in macros:
            for e in events:
                for sig in signals:
                    if m in s or e in s or sig in s:
                        conf, reason = confidence(s, m, e, sig)
                        if conf != "LOW":
                            links.append((m, e, sig, conf, reason))

    # Deduplicate
    links = list({(m,e,s,c):r for m,e,s,c,r in links}.items())

    # CSV export
    csv_path = out / "macro_event_signal_links.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Macro", "Event", "Signal", "Confidence", "Context"])
        for (m,e,s,c), reason in links:
            w.writerow([m, e, s, c, reason])

    # Markdown generation (summary only)
    for m in macros:
        used = [(e,s,c) for (mm,e,s,c),_ in links if mm == m]
        text = f"# Macro: {m}\n\n## Links\n"
        for e,s,c in used:
            text += f"- Event: {e}, Signal: {s}, Confidence: {c}\n"
        (macros_dir / f"{m}.md").write_text(text)

    print("✅ Extraction with confidence complete")

    report = generate_html_report(
    out,
    sdf.name,
    macros,
    events,
    signals,
    links
)

print(f"📄 HTML report: {report}")


if __name__ == "__main__":
    main()