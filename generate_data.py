"""Generate clearly labelled synthetic demo data for SURYA-R."""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)
rng = np.random.default_rng(42)
n = 1800
irr = rng.uniform(150, 1050, n)
ambient = rng.uniform(18, 45, n)
panel_temp = ambient + (irr / 1000) * rng.uniform(12, 28, n)
# Illustrative 5 kW section with a simple temperature coefficient.
clean_power = 5.0 * (irr / 1000) * (1 - 0.004 * (panel_temp - 25))
clean_power = np.maximum(clean_power, 0) + rng.normal(0, 0.06, n)
clean_power = np.maximum(clean_power, 0)
clean = pd.DataFrame({
    "irradiance_w_m2": irr.round(1),
    "panel_temp_c": panel_temp.round(1),
    "ambient_temp_c": ambient.round(1),
    "clean_power_kw": clean_power.round(3),
})
clean.to_csv(DATA / "synthetic_clean_panel_data.csv", index=False)

sections = []
for i in range(1, 9):
    ir = float(rng.uniform(450, 950))
    amb = float(rng.uniform(24, 42))
    pt = amb + ir / 1000 * float(rng.uniform(14, 25))
    expected = max(0, 5.0 * ir / 1000 * (1 - 0.004 * (pt - 25)))
    # Simulated shortfall; this is not measured soiling data.
    shortfall = float(rng.uniform(0.01, 0.24))
    observed = max(0, expected * (1 - shortfall) + rng.normal(0, 0.025))
    sections.append({
        "section_id": f"Section {i}",
        "irradiance_w_m2": round(ir, 1),
        "panel_temp_c": round(pt, 1),
        "ambient_temp_c": round(amb, 1),
        "observed_power_kw": round(observed, 3),
        "synthetic_shortfall_for_demo_only": round(shortfall, 3),
    })
pd.DataFrame(sections).to_csv(DATA / "synthetic_sections_demo.csv", index=False)
print(f"Created synthetic demo data in {DATA}")
