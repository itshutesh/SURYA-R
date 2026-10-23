"""Transparent rule-based maintenance comparison for the SURYA-R demo."""


def compare_maintenance(
    expected_power_kw: float,
    observed_power_kw: float,
    hours_remaining: float,
    electricity_price_per_kwh: float,
    water_litres: float,
    water_cost_per_litre: float,
    labour_cost: float,
    recovery_fraction: float,
    water_budget_litres: float,
):
    expected = max(0.0, expected_power_kw)
    observed = max(0.0, observed_power_kw)
    loss_kw = max(0.0, expected - observed)
    loss_pct = (loss_kw / expected * 100.0) if expected > 0 else 0.0
    recoverable_kw = loss_kw * min(1.0, max(0.0, recovery_fraction))
    recovered_kwh = recoverable_kw * max(0.0, hours_remaining)
    energy_value = recovered_kwh * max(0.0, electricity_price_per_kwh)
    water_cost = max(0.0, water_litres) * max(0.0, water_cost_per_litre)
    total_cost = water_cost + max(0.0, labour_cost)
    net_benefit = energy_value - total_cost
    within_budget = water_litres <= water_budget_litres

    if expected <= 0:
        recommendation = "Collect valid sunlight and power readings"
        reason = "Expected output is zero or unavailable, so a loss estimate is not meaningful."
    elif loss_pct < 5:
        recommendation = "Monitor; cleaning is not currently justified by this rule"
        reason = "Estimated output shortfall is below the prototype's 5% screening threshold."
    elif not within_budget:
        recommendation = "Inspect or consider a lower-water method"
        reason = "The proposed cleaning exceeds the available water budget."
    elif net_benefit > 0:
        recommendation = "Cleaning may be worthwhile; verify before action"
        reason = "Estimated energy value exceeds estimated cleaning cost under the chosen assumptions."
    else:
        recommendation = "Wait or inspect before cleaning"
        reason = "Estimated energy value does not exceed estimated cleaning cost under the chosen assumptions."

    return {
        "loss_kw": loss_kw,
        "loss_pct": loss_pct,
        "recoverable_kw": recoverable_kw,
        "recovered_kwh": recovered_kwh,
        "energy_value": energy_value,
        "water_cost": water_cost,
        "total_cost": total_cost,
        "net_benefit": net_benefit,
        "within_budget": within_budget,
        "recommendation": recommendation,
        "reason": reason,
    }
