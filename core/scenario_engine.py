"""
FieldShift Climate Scenario Simulator Engine.
Implements sensitivity what-if stress tests, daily series transformations,
FAO-56 Hargreaves-Samani Reference Evapotranspiration (ET0), and rescoring comparisons.
"""

import math
import numpy as np
import pandas as pd
from core.agronomy_engine import generate_and_score_rotations, evaluate_baseline_monoculture

SCENARIO_PRESETS = {
    "Historical Baseline": {
        "temp_anomaly_c": 0.0,
        "rain_change_pct": 0.0,
        "irrigation_pct": 100,
        "onset_delay_weeks": 0,
        "dry_spell_shift": 0.0,
        "description": "Historical 15-year NASA POWER climate averages without anomaly perturbations."
    },
    "Moderate Drought & Warming (+1.5°C, -20% Rain)": {
        "temp_anomaly_c": 1.5,
        "rain_change_pct": -20.0,
        "irrigation_pct": 100,
        "onset_delay_weeks": 1,
        "dry_spell_shift": 2.0,
        "description": "Simulates moderate semi-arid intensification with prolonged dry spells."
    },
    "Severe Heat Stress (+3.0°C, -10% Rain)": {
        "temp_anomaly_c": 3.0,
        "rain_change_pct": -10.0,
        "irrigation_pct": 100,
        "onset_delay_weeks": 0,
        "dry_spell_shift": 3.0,
        "description": "Simulates severe reproductive heat wave frequency during summer anthesis."
    },
    "Delayed Monsoon / Season Onset (3 Weeks Late)": {
        "temp_anomaly_c": 0.8,
        "rain_change_pct": -15.0,
        "irrigation_pct": 100,
        "onset_delay_weeks": 3,
        "dry_spell_shift": 2.5,
        "description": "Simulates seasonal monsoon lag forcing delayed germination and early moisture stress."
    },
    "Restricted Irrigation Allocation (50% Water Limit)": {
        "temp_anomaly_c": 0.5,
        "rain_change_pct": -10.0,
        "irrigation_pct": 50,
        "onset_delay_weeks": 0,
        "dry_spell_shift": 1.0,
        "description": "Simulates strict groundwater extraction caps and canal water rationing."
    },
    "Extreme Wet / Deluge (+35% Rain, High Volatility)": {
        "temp_anomaly_c": 0.2,
        "rain_change_pct": 35.0,
        "irrigation_pct": 100,
        "onset_delay_weeks": 0,
        "dry_spell_shift": -1.5,
        "description": "Simulates elevated precipitation volume testing waterlogging and residue resilience."
    },
    "Hypothetical 2040 (User-Defined Sensitivity)": {
        "temp_anomaly_c": 2.2,
        "rain_change_pct": -18.0,
        "irrigation_pct": 75,
        "onset_delay_weeks": 2,
        "dry_spell_shift": 3.5,
        "description": "Compound warming and rainfall retraction what-if sensitivity (NOT an official IPCC projection)."
    }
}

def calculate_hargreaves_et0(lat: float, temp_c: float, dtr: float = 12.0) -> float:
    """
    Computes annual reference evapotranspiration (ET0 mm/yr) using the FAO-56 Hargreaves-Samani method:
    ET0 = 0.0023 * Ra * (Tmean + 17.8) * sqrt(Tmax - Tmin)
    Where Ra is mean extraterrestrial radiation estimated from latitude.
    """
    # Mean annual extraterrestrial solar radiation (mm/day equivalent)
    ra_mean = max(5.0, 15.5 - 0.12 * abs(lat))
    et0_daily = 0.0023 * ra_mean * (temp_c + 17.8) * math.sqrt(max(1.0, dtr))
    return max(300.0, round(et0_daily * 365.25, 1))

def apply_climate_scenario(
    baseline_climate: dict,
    lat: float,
    temp_anomaly_c: float,
    rain_change_pct: float,
    irrigation_pct: int,
    onset_delay_weeks: int,
    dry_spell_shift: float
) -> dict:
    """
    Transforms baseline climate indicators and annual series using scenario parameters.
    """
    base_series = baseline_climate.get("annual_series", [])
    transformed_series = []
    
    rain_mult = max(0.2, 1.0 + (rain_change_pct / 100.0))
    
    for rec in base_series:
        y_rain = max(50.0, round(rec["rain"] * rain_mult, 1))
        y_temp = round(rec["temp"] + temp_anomaly_c, 1)
        # Heat days scale non-linearly with temperature shifts
        y_hot = max(0, int(round(rec["hot_days"] * max(0.1, 1.0 + (temp_anomaly_c * 0.35)))))
        y_dry = max(0.5, round(rec.get("dry_spells", 2.0) + dry_spell_shift, 1))
        
        transformed_series.append({
            "year": rec["year"],
            "rain": y_rain,
            "temp": y_temp,
            "hot_days": y_hot,
            "dry_spells": y_dry
        })

    df_trans = pd.DataFrame(transformed_series)
    mean_rain = float(df_trans["rain"].mean())
    mean_temp = float(df_trans["temp"].mean())
    avg_hot = int(df_trans["hot_days"].mean())
    avg_dry = float(df_trans["dry_spells"].mean())
    
    years_arr = df_trans["year"].values
    rain_slope = float(np.polyfit(years_arr, df_trans["rain"].values, 1)[0])
    temp_slope = float(np.polyfit(years_arr, df_trans["temp"].values, 1)[0])

    et0 = calculate_hargreaves_et0(lat, mean_temp)
    climatic_water_deficit = round(mean_rain - et0, 1)

    return {
        "source": "SIMULATED SCENARIO (Sensitivity Model)",
        "provenance": "MODELED / SIMULATED",
        "mean_annual_rainfall_mm": round(mean_rain, 1),
        "rainfall_trend_pct": round((rain_slope * 10 / max(mean_rain, 1)) * 100, 1),
        "mean_annual_temp_c": round(mean_temp, 1),
        "warming_rate_c_decade": round(temp_slope * 10, 2),
        "hot_days_per_year": avg_hot,
        "dry_spells_per_year": round(avg_dry, 1),
        "annual_series": transformed_series,
        "reference_et0_mm": et0,
        "climatic_water_deficit_mm": climatic_water_deficit,
        "irrigation_availability_pct": irrigation_pct,
        "onset_delay_weeks": onset_delay_weeks
    }

def rescore_rotations_under_scenario(
    crop_df: pd.DataFrame,
    past_crops: list,
    weights: dict,
    scenario_climate: dict,
    soil_data: dict,
    baseline_rotations: list
) -> list:
    """
    Re-scores rotation candidates under the altered climate parameters and computes ranking deltas.
    """
    scenario_candidates = generate_and_score_rotations(
        crop_df=crop_df,
        past_crops=past_crops,
        weights=weights,
        climate_data=scenario_climate,
        soil_data=soil_data
    )
    
    # Map baseline rank
    baseline_rank_map = {tuple(r["crops"]): (i + 1, r["composite_score"]) for i, r in enumerate(baseline_rotations)}
    
    rescored_results = []
    for sc_rank, sc_rot in enumerate(scenario_candidates[:5]):
        key = tuple(sc_rot["crops"])
        b_info = baseline_rank_map.get(key, (None, None))
        b_rank, b_score = b_info
        
        score_delta = round(sc_rot["composite_score"] - b_score, 1) if b_score is not None else 0.0
        rank_delta = (b_rank - (sc_rank + 1)) if b_rank is not None else 0
        
        # Calculate water deficit under scenario
        irrig_avail = scenario_climate.get("irrigation_availability_pct", 100) / 100.0
        unmet_deficit = max(0, int(sc_rot["annual_water_need_mm"] - (scenario_climate["mean_annual_rainfall_mm"] + 200 * irrig_avail)))
        
        rescored_results.append({
            **sc_rot,
            "scenario_rank": sc_rank + 1,
            "baseline_rank": b_rank,
            "score_delta": score_delta,
            "rank_delta": rank_delta,
            "unmet_water_deficit_mm": unmet_deficit
        })
        
    return rescored_results
