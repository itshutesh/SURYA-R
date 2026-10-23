# SURYA-R: Water-Aware Solar Maintenance Intelligence

A laptop-only Streamlit prototype for exploring solar output shortfalls and water-aware maintenance decisions.

## Important limitations
- Included datasets are synthetic and explicitly for demonstration.
- The Random Forest model predicts output from synthetic clean-panel examples. Its test metrics are not evidence of real-world accuracy.
- Expected-minus-observed output is a performance shortfall, not a direct measurement of dust/soiling.
- Water costs, cleaning costs, recoverable fraction and the 5% screening threshold are user-adjustable assumptions, not validated recommendations.
- Do not use the prototype as an autonomous instruction to clean a live solar installation.

## Run on Windows

Open this folder in VS Code, then in its terminal run:

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python generate_data.py
streamlit run app.py
```

If `python` is not recognized, use `py` in the environment creation command and check that Python is added to PATH.

The dashboard should open in your browser, usually at `http://localhost:8501`.

## Files
- `app.py`: Streamlit dashboard
- `model.py`: baseline Random Forest expected-output model
- `decision_engine.py`: transparent cost/water decision rules
- `generate_data.py`: reproducible synthetic data generator
- `data/`: generated synthetic datasets

## Next research steps
1. Review literature on PV soiling estimation and cleaning optimization.
2. Find a documented, suitable real dataset or design a controlled measurement study.
3. Compare against fixed-interval and threshold-based baselines.
4. Evaluate prediction error, energy recovered, water per recovered kWh, cost, and robustness.
