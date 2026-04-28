# Tooling Overview

## extract_macros_from_sdf.py
Safely extracts macro name, autostart flag, and command count from the SDF.

## validate_events_vs_macros.py
Fails if events reference macros that do not exist.

## validate_gui_vs_ldf.py
Warns if GUI uses LIN signals not present in the LDF.

## generate_html_report.py
Creates a fully linked HTML overview of:
- Macros
- Events → Macros
- GUI Widgets → Signals