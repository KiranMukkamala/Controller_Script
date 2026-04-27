# SDF Heuristic Extraction & Documentation Tool

## Overview

This tool provides **best-effort, read-only extraction** of human-relevant information from **LIN SessionConf `.sdf` files**.

It is designed to help with:

- ✅ Documentation of legacy SDF configurations  
- ✅ Traceability (GUI → Macro → Event → Signal)  
- ✅ Code reviews and handovers  
- ✅ Regression detection between SDF versions  
- ✅ CI / quality gates  

⚠️ **Important**  
This tool **does not decode SDF internals** and **does not modify SDF files**.  
All extraction is **heuristic and confidence-scored**.

---

## What the Tool Extracts

From an SDF file, the tool attempts to identify:

- **Metadata** (project name, versions, build strings)
- **Macros** (macro names and usage relationships)
- **Events** (startup, power, ignition, and other event names)
- **Signals** (LIN, virtual, or system signal identifiers)
- **GUI elements** (buttons, sliders, checkboxes, panels, menus)

It also infers **relationships** between these items and assigns a **confidence level**.

---

## Confidence Levels

| Confidence | Meaning | Action |
|----------|--------|--------|
| HIGH | Strong textual proximity | Quick sanity check |
| MEDIUM | Partial evidence | Verify in SessionConf |
| LOW | Weak heuristic | Must be reviewed manually |

---

## Generated Outputs

### CSV Output
- File: `sdf_links.csv`
- Purpose: CI checks, automation, audits, diffing

### Markdown Output

- `section_metadata.md`
- `section_macros.md`
- `section_events.md`
- `section_signals.md`
- `section_gui.md`

Purpose: Engineer-readable documentation and Git diffs.

### HTML Report

- File: `sdf_extraction_report.html`
- Includes:
  - Overview statistics
  - Confidence-colored tables
  - GUI → Macro → Signal view

Open directly in a browser; no server required.

---

## Requirements

- Python 3.8 or newer
- Access to the `.sdf` file

No LIN SessionConf installation required.

---

## Usage

```bash
python extract_sdf_artifacts_with_confidence.py <input.sdf> <output_dir>
```

### Example

```bash
python tools/extract_sdf_artifacts_with_confidence.py sdf/wiper_simulation.sdf out/
```

The output directory will be created automatically if it does not exist.

---

## Recommended Workflow

1. Run the tool for every important SDF
2. Commit generated CSV, Markdown, and HTML together with the SDF
3. Review HTML report before releases
4. Treat LOW confidence items as mandatory verification tasks

---

## What This Tool Does NOT Do

- ❌ Decode the binary SDF format
- ❌ Reconstruct macro logic
- ❌ Rebuild GUI layouts
- ❌ Replace LIN SessionConf

This tool is strictly a **documentation and traceability assistant**.

---

## Safety & Responsibility

For safety-critical or production-critical behavior, always verify results directly in **LIN SessionConf**.

---

## License / Usage

Internal engineering utility. No warranty.

---

## Questions or Extensions

Possible future extensions:
- HTML diff between two SDF reports
- GUI operator-risk scoring
- CI confidence regression checks
- Graphical macro/event diagrams

