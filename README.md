
# SessionConf Documentation
This repository documents and validates SessionConf 2.40.x projects.

## Why this exists
SessionConf 2.40.x does not support exporting Events or GUI definitions.
This toolkit creates **auditable documentation** by combining:
- SDF macro metadata
- LDF signal definitions
- Manually documented CSV files (Events, GUI)

## Data sources
- `inputs/sdf`  → Macro metadata
- `inputs/ldf`  → LIN signal definitions
- `inputs/events/events.csv` → Event → Macro mappings (manual)
- `inputs/gui/gui_widgets.csv` → GUI → Signal mappings (manual)


## Folder Structure

Controller_Script/
├─ inputs/
│  ├─ sdf/
│  ├─ ldf/
│  ├─ events/
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

