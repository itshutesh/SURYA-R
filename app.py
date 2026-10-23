from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
from model import train_baseline, predict_expected_power
from decision_engine import compare_maintenance

ROOT = Path(__file__).resolve().parent
CLEAN_DATA = ROOT / "data" / "synthetic_clean_panel_data.csv"
SECTIONS_DATA = ROOT / "data" / "synthetic_sections_demo.csv"

st.set_page_config(page_title="SURYA-R | Solar Maintenance Intelligence", page_icon="☀️", layout="wide")
st.title("☀️ SURYA-R")
st.subheader("Water-Aware Solar Maintenance Intelligence")
st.warning("Prototype notice: the included data are synthetic and illustrative. Recommendations are decision-support examples, not operational instructions. A power shortfall does not prove dust/soiling; shading, faults, weather and measurement errors can also cause it.")

if not CLEAN_DATA.exists() or not SECTIONS_DATA.exists():
    st.error("Demo data files are missing. Run `python generate_data.py` in the project terminal.")
    st.stop()

clean_df = pd.read_csv(CLEAN_DATA)
sections_df = pd.read_csv(SECTIONS_DATA)
model, metrics = train_baseline(clean_df)

with st.sidebar:
    st.header("Site assumptions")
    electricity_price = st.number_input("Electricity value (₹/kWh)", min_value=0.0, value=6.0, step=0.5)
    water_litres = st.number_input("Water for one cleaning (litres)", min_value=0.0, value=20.0, step=5.0)
    water_cost = st.number_input("Water cost (₹/litre)", min_value=0.0, value=0.05, step=0.01, format="%.2f")
    labour_cost = st.number_input("Labour/other cost (₹)", min_value=0.0, value=35.0, step=5.0)
    water_budget = st.number_input("Available water budget (litres)", min_value=0.0, value=100.0, step=10.0)
    recovery_fraction = st.slider("Assumed recoverable share of estimated shortfall", 0.0, 1.0, 0.65, 0.05)
    hours_remaining = st.slider("Useful generation hours remaining", 1, 12, 5)

st.caption("Baseline model: Random Forest trained on simulated clean-panel data. Metrics below describe only the synthetic hold-out test, not real-world performance.")
m1, m2, m3 = st.columns(3)
m1.metric("Synthetic test MAE", f"{metrics['mae_kw']:.3f} kW")
m2.metric("Synthetic test R²", f"{metrics['r2']:.3f}")
m3.metric("Training rows", f"{len(clean_df) - metrics['test_rows']:,}")

st.header("1. Section-level assessment")
results = []
for _, row in sections_df.iterrows():
    expected = predict_expected_power(model, row.irradiance_w_m2, row.panel_temp_c, row.ambient_temp_c)
    decision = compare_maintenance(
        expected_power_kw=expected,
        observed_power_kw=float(row.observed_power_kw),
        hours_remaining=hours_remaining,
        electricity_price_per_kwh=electricity_price,
        water_litres=water_litres,
        water_cost_per_litre=water_cost,
        labour_cost=labour_cost,
        recovery_fraction=recovery_fraction,
        water_budget_litres=water_budget,
    )
    results.append({
        "Section": row.section_id,
        "Irradiance (W/m²)": row.irradiance_w_m2,
        "Panel temp (°C)": row.panel_temp_c,
        "Expected power (kW)": round(expected, 3),
        "Observed power (kW)": row.observed_power_kw,
        "Estimated shortfall (%)": round(decision["loss_pct"], 1),
        "Estimated recovery (kWh)": round(decision["recovered_kwh"], 3),
        "Net benefit (₹)": round(decision["net_benefit"], 2),
        "Recommendation": decision["recommendation"],
        "Reason": decision["reason"],
    })
results_df = pd.DataFrame(results).sort_values("Estimated shortfall (%)", ascending=False)
st.dataframe(results_df, use_container_width=True, hide_index=True)

fig = px.bar(results_df.sort_values("Section"), x="Section", y=["Expected power (kW)", "Observed power (kW)"], barmode="group", title="Expected vs observed output (simulated sections)")
st.plotly_chart(fig, use_container_width=True)

st.header("2. Try your own operating conditions")
left, right = st.columns(2)
with left:
    irradiance = st.slider("Sunlight / irradiance (W/m²)", 100, 1100, 750, 25)
    ambient = st.slider("Ambient temperature (°C)", 0, 50, 32)
    panel_temp = st.slider("Panel temperature (°C)", 0, 85, 52)
with right:
    observed = st.number_input("Observed section output (kW)", min_value=0.0, max_value=5.0, value=3.0, step=0.1)
    st.caption("This prototype assumes a nominal 5 kW section. Use plausible inputs and remember that synthetic data are not a substitute for site measurements.")
expected = predict_expected_power(model, irradiance, panel_temp, ambient)
decision = compare_maintenance(expected, observed, hours_remaining, electricity_price, water_litres, water_cost, labour_cost, recovery_fraction, water_budget)

c1, c2, c3 = st.columns(3)
c1.metric("Modelled expected power", f"{expected:.2f} kW")
c2.metric("Estimated shortfall", f"{decision['loss_pct']:.1f}%", f"{decision['loss_kw']:.2f} kW")
c3.metric("Estimated net benefit", f"₹{decision['net_benefit']:.2f}")
st.subheader(decision["recommendation"])
st.write(decision["reason"])
st.write(f"Estimated energy value: ₹{decision['energy_value']:.2f} | Estimated cleaning cost: ₹{decision['total_cost']:.2f} | Water budget respected: {'Yes' if decision['within_budget'] else 'No'}")
st.info("Interpretation limit: expected-minus-observed output is a performance shortfall, not a dust measurement. Before cleaning, validate sensors and check shading, inverter/electrical faults, weather and soiling evidence. The 5% screening threshold and recovery fraction are configurable prototype assumptions, not validated thresholds.")

st.header("3. Export results")
st.download_button("Download section assessment CSV", data=results_df.to_csv(index=False).encode("utf-8"), file_name="surya_r_section_assessment.csv", mime="text/csv")
st.caption("SURYA-R research prototype • Synthetic demo data • No real plant data loaded")
