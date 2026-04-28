import sys
from pathlib import Path

# --- FIX ---
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from tools.utils.common import read_csv, resolve_input_file

GUI_DIR = Path("inputs/gui")
LDF_DIR = Path("inputs/ldf")

def parse_ldf_signals(path):
    signals = set()
    for line in path.read_text(errors="ignore").splitlines():
        if ":" in line and ";" in line:
            name = line.split(":")[0].strip()
            if name.isidentifier():
                signals.add(name)
    return signals

def main():
    gui_csv = resolve_input_file(
        GUI_DIR, ["csv"], "GUI CSV", yaml_key="gui"
    )
    ldf_file = resolve_input_file(
        LDF_DIR, ["ldf"], "LDF file", yaml_key="ldf"
    )

    gui = read_csv(gui_csv)
    ldf_signals = parse_ldf_signals(ldf_file)

    for w in gui:
        if w["SignalOrigin"] == "LIN" and w["Signal"] not in ldf_signals:
            print(f"⚠️ GUI uses LIN signal not in LDF: {w['Signal']}")

    print("✅ GUI vs LDF check completed")

if __name__ == "__main__":
    main()