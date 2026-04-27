#!/usr/bin/env python3
"""
SDF Heuristic Extractor & Documentation Generator (Macro-Prefix Aware)
---------------------------------------------------------------------

Purpose
-------
Best-effort, read-only extraction of documentation-relevant information
from LIN SessionConf SDF files.

Key Design Points
-----------------
- This tool is NOT a binary SDF decoder.
- It relies on printable strings and naming conventions.
- The macro_ prefix is treated as an authoritative signal.
- Confidence is explicit: HIGH / MEDIUM / LOW.
- Output is for documentation, review, and CI – not execution.

Generated outputs
-----------------
- sdf_links.csv                (machine/CI readable)
- section_*.md                 (engineer readable)
- sdf_extraction_report.html   (reviewer readable, includes GUI view)
"""

import re
import sys
import csv
from pathlib import Path
from collections import Counter

# =====================================================================
# PROJECT CONFIGURATION
# =====================================================================

# Explicit macro naming convention used in the SDF
MACRO_PREFIX = "macro_"

# Enable fallback heuristic detection for legacy macros
ALLOW_FALLBACK_MACROS = False  # set True only if needed

# GUI keywords to avoid false macro detection
GUI_HINTS = [
    "button", "btn", "menu", "panel",
    "slider", "checkbox", "check", "click", "press"
]

# =====================================================================
# STRING EXTRACTION
# =====================================================================

def extract_strings(binary_blob, min_len=4):
    """
    Extract printable ASCII strings from binary data.
    This is the foundation of all heuristic analysis.
    """
    pattern = rb"[ -~]{%d,}" % min_len
    return [
        s.decode("ascii", errors="ignore")
        for s in re.findall(pattern, binary_blob)
    ]

# =====================================================================
# MACRO DETECTION LOGIC
# =====================================================================

def looks_like_legacy_macro(name: str) -> bool:
    """
    Heuristic fallback for legacy macros (optional).
    Used only if ALLOW_FALLBACK_MACROS is enabled.
    """
    if any(h in name.lower() for h in GUI_HINTS):
        return False

    patterns = [
        r"^[A-Z][A-Za-z0-9_]{4,}$",   # PascalCase
        r"^[A-Z0-9_]{5,}$",           # UPPER_SNAKE_CASE
    ]
    return any(re.match(p, name) for p in patterns)

def is_macro_name(name: str) -> bool:
    """
    Determine whether a string represents a macro name.
    Priority:
      1. macro_ prefix (authoritative, HIGH confidence)
      2. fallback heuristic (optional, lower confidence)
    """
    if name.startswith(MACRO_PREFIX):
        return True

    if ALLOW_FALLBACK_MACROS and looks_like_legacy_macro(name):
        return True

    return False

def macro_base_confidence(name: str) -> str:
    """
    Base confidence purely from naming convention.
    """
    if name.startswith(MACRO_PREFIX):
        return "HIGH"
    return "MEDIUM"

# =====================================================================
# SECTION CLASSIFICATION
# =====================================================================

def classify_sections(strings):
    """
    Classify extracted strings into logical SDF sections.
    """
    sections = {
        "metadata": set(),
        "macros": set(),
        "events": set(),
        "signals": set(),
        "gui": set(),
    }

    for s in strings:
        sl = s.lower()

        # Metadata
        if any(k in sl for k in ["version", "project", "build", "author"]):
            sections["metadata"].add(s)
            continue

        # Macros (prefix-first)
        if is_macro_name(s):
            sections["macros"].add(s)
            continue

        # Events
        if any(k in sl for k in ["event", "startup", "power", "ignition"]):
            sections["events"].add(s)
            continue

        # Signals
        if s.isupper() and 2 < len(s) < 32:
            sections["signals"].add(s)
            continue

        # GUI elements
        if any(k in sl for k in GUI_HINTS + ["gui"]):
            sections["gui"].add(s)
            continue

    return sections

# =====================================================================
# CONFIDENCE UTILS
# =====================================================================

CONF_RANK = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}

def upgrade_confidence(a, b):
    """Return the stronger of two confidence levels."""
    return a if CONF_RANK[a] >= CONF_RANK[b] else b

def proximity_confidence(text, *tokens):
    """
    Determine confidence from textual proximity.
    """
    hits = [t for t in tokens if t and t in text]
    if len(hits) == len(tokens):
        return "HIGH"
    if len(hits) >= 2:
        return "MEDIUM"
    return "LOW"

# =====================================================================
# RELATIONSHIP EXTRACTION
# =====================================================================

def extract_links(strings, sections):
    """
    Extract macro-event-signal-gui relationships with confidence.
    """
    links = []

    # Frequency tracking (reinforces confidence)
    macro_hits = Counter()
    for line in strings:
        for m in sections["macros"]:
            if m in line:
                macro_hits[m] += 1

    for line in strings:
        # Macro ↔ Event ↔ Signal
        for m in sections["macros"]:
            for e in sections["events"]:
                for s in sections["signals"]:
                    prox = proximity_confidence(line, m, e, s)
                    if prox == "LOW":
                        continue

                    conf = upgrade_confidence(
                        macro_base_confidence(m),
                        prox
                    )

                    links.append({
                        "macro": m,
                        "event": e,
                        "signal": s,
                        "gui": "",
                        "confidence": conf,
                        "context": "Macro/Event/Signal proximity"
                    })

        # GUI ↔ Macro (project-safe because of prefix)
        for gui in sections["gui"]:
            for m in sections["macros"]:
                prox = proximity_confidence(line, gui, m)
                if prox == "LOW":
                    continue

                conf = upgrade_confidence(
                    macro_base_confidence(m),
                    prox
                )

                links.append({
                    "macro": m,
                    "event": "",
                    "signal": "",
                    "gui": gui,
                    "confidence": conf,
                    "context": "GUI triggers macro"
                })

    return links

# =====================================================================
# OUTPUT: CSV
# =====================================================================

def write_csv(out_dir, links):
    csv_path = out_dir / "sdf_links.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["macro", "event", "signal", "gui", "confidence", "context"]
        )
        writer.writeheader()
        for l in links:
            writer.writerow(l)

# =====================================================================
# OUTPUT: MARKDOWN
# =====================================================================

def write_section_markdown(out_dir, sections, sdf_name):
    for section, items in sections.items():
        md = out_dir / f"section_{section}.md"
        with md.open("w", encoding="utf-8") as f:
            f.write(f"# {section.upper()} SECTION\n\n")
            f.write(f"Extracted from: `{sdf_name}`\n\n")
            for i in sorted(items):
                f.write(f"- {i}\n")

# =====================================================================
# OUTPUT: HTML REPORT (WITH GUI VIEW)
# =====================================================================

def generate_html_report(out_dir, sdf_name, sections, links):
    def cls(c): return f"conf-{c}"

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>SDF Extraction Report – {sdf_name}</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 20px; }}
table {{ border-collapse: collapse; width: 100%; margin-bottom: 25px; }}
th, td {{ border: 1px solid #ccc; padding: 6px; }}
th {{ background-color: #f0f0f0; }}
.conf-HIGH {{ background-color: #d4edda; }}
.conf-MEDIUM {{ background-color: #fff3cd; }}
.conf-LOW {{ background-color: #f8d7da; }}
.small {{ font-size: 0.9em; color: #555; }}
</style>
</head>
<body>

<h1>SDF Extraction Report</h1>
<p class="small">
Source: <b>{sdf_name}</b><br>
macro_ prefix is treated as authoritative.
</p>

<h2>Overview</h2>
<ul>
<li>Macros: {len(sections["macros"])}</li>
<li>Events: {len(sections["events"])}</li>
<li>Signals: {len(sections["signals"])}</li>
<li>GUI Elements: {len(sections["gui"])}</li>
<li>Total Links: {len(links)}</li>
</ul>

<h2>Macro ↔ Event ↔ Signal</h2>
<table>
<tr><th>Macro</th><th>Event</th><th>Signal</th><th>Confidence</th></tr>
"""
    for l in links:
        if l["event"] or l["signal"]:
            html += f"""
<tr class="{cls(l["confidence"])}">
<td>{l["macro"]}</td>
<td>{l["event"]}</td>
<td>{l["signal"]}</td>
<td>{l["confidence"]}</td>
</tr>"""

    html += """
</table>

<h2>GUI → Macro</h2>
<table>
<tr><th>GUI Element</th><th>Macro</th><th>Confidence</th></tr>
"""
    for l in links:
        if l["gui"]:
            html += f"""
<tr class="{cls(l["confidence"])}">
<td>{l["gui"]}</td>
<td>{l["macro"]}</td>
<td>{l["confidence"]}</td>
</tr>"""

    html += """
</table>
</body></html>
"""

    path = out_dir / "sdf_extraction_report.html"
    path.write_text(html, encoding="utf-8")

# =====================================================================
# MAIN
# =====================================================================

def main():
    if len(sys.argv) != 3:
        print("Usage: python extract_sdf_with_html_report.py <input.sdf> <output_dir>")
        sys.exit(1)

    sdf = Path(sys.argv[1])
    out = Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)

    strings = extract_strings(sdf.read_bytes())
    sections = classify_sections(strings)
    links = extract_links(strings, sections)

    write_csv(out, links)
    write_section_markdown(out, sections, sdf.name)
    generate_html_report(out, sdf.name, sections, links)

    print("✅ Extraction complete")
    for k, v in sections.items():
        print(f"  {k:10}: {len(v)}")

if __name__ == "__main__":
    main()