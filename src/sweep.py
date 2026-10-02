"""Sweep policy threshold -> energy vs accuracy trade-off table (written to results/sweep.md)."""
import subprocess, json, re, pathlib
p = pathlib.Path("src/adaptive_policy.py"); orig = p.read_text()
rows = ["| threshold | windows sent | energy saved | accuracy |", "|---|---|---|---|"]
try:
    for t in [0.0, 0.5, 0.6, 0.7, 0.75, 0.85]:
        p.write_text(re.sub(r"base_thresh: float = [0-9.]+", f"base_thresh: float = {t}", orig))
        subprocess.run(["python", "src/simulate.py"], capture_output=True)
        m = json.load(open("results/system_metrics.json"))
        rows.append(f"| {t} | {m['windows_transmitted']}/{m['windows']} | {m['energy_reduction_pct']:.1f}% | {m['end_to_end_accuracy_pct']:.1f}% |")
finally:
    p.write_text(orig)
open("results/sweep.md", "w").write("\n".join(rows)); print("\n".join(rows))
