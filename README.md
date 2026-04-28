
# SessionConf Macro Documentation Toolchain

This repository provides an end‑to‑end toolchain for extracting, validating,
and documenting SessionConf macros with full, verifiable fidelity.

## Purpose

- Convert SessionConf macro configuration into auditable documentation
- Preserve exact macro step ordering (1 SessionConf row = 1 CSV row)
- Provide automated validation to prevent documentation drift
- Generate human‑readable HTML with deep links to macro steps
- SessionConf 2.40.x does not support exporting Events or GUI definitions.
- This toolkit creates **auditable documentation** by combining:
- SDF macro metadata
- LDF signal definitions
- Manually documented CSV files (Events, GUI)

## Data sources
- `inputs/sdf`  → Macro metadata
- `inputs/ldf`  → LIN signal definitions
- `inputs/sdf/`
  - SessionConf `.sdf` export files
- `inputs/macros/macro_steps.csv`
  - Authoritative macro step transcription
- `inputs/macros/macro_event_links.csv`
  - Macro ↔ event / service mapping
- `inputs/events/events.csv` → Event → Macro mappings (manual)
- `inputs/gui/gui_widgets.csv` → GUI → Signal mappings (manual)


## Folder Structure

Controller_Script/
├─ inputs/
│  ├─ sdf/
│  ├─ ldf/
│  ├─ events/
│  ├─ macros/
│  ├─ gui/
│  └─ metadata/
│     └─ project.yaml
│
├─ tools/
│  ├─ extract_macros/
│  ├─ validate/
│  ├─ report/
│  └─ utils/
│
├─ scripts/
│  └─ run_all.bat
│
├─ outputs/
│  └─ run_YYYYMMDD_HHMMSS/


## Outputs

- `outputs/html/index.html`
  - Macro index page
- `outputs/html/macros/*.html`
  - One HTML page per macro with step anchors
- `outputs/html/verification_report.html`
  - Final consistency and coverage report

## Running the Toolchain

Use the single entry point:

```bat
scripts\run_all.bat
