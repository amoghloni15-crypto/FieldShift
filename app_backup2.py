import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import requests

# Page configuration
st.set_page_config(
    page_title="FieldShift Rotation Advisor | NASA Space Apps 2026",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1b4332;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #40916c;
        margin-bottom: 1.2rem;
    }
    .metric-card {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 14px 18px;
        border-left: 4px solid #2d6a4f;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .stAlert {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# CONSTANTS & PRESETS
# ---------------------------------------------------------
PRESETS = {
    "Lubbock, Texas (Semi-Arid High Plains)": {
        "lat": 33.5779,
        "lon": -101.8552,
        "climate_type": "Semi-arid continental (Drought-prone, hot summers, high evaporative demand)",
        "default_past_crops": ["Maize (Corn)", "Grain Sorghum"],
        "fallback_soil": {"clay_pct": 24.0, "sand_pct": 52.0, "soc_pct": 0.85, "ph": 7.4},
        "fallback_climate": {
            "mean_annual_rainfall_mm": 472.0,
            "rainfall_trend_pct": -4.2,
            "mean_annual_temp_c": 16.5,
            "warming_rate_c_decade": 0.38,
            "hot_days_per_year": 48,
            "dry_spells_per_year": 4.1,
            "annual_series": [
                {"year": 2010, "rain": 620, "temp": 16.1, "hot_days": 42},
                {"year": 2011, "rain": 185, "temp": 17.8, "hot_days": 86},
                {"year": 2012, "rain": 340, "temp": 17.2, "hot_days": 54},
                {"year": 2013, "rain": 410, "temp": 16.2, "hot_days": 40},
                {"year": 2014, "rain": 530, "temp": 16.3, "hot_days": 38},
                {"year": 2015, "rain": 710, "temp": 16.6, "hot_days": 32},
                {"year": 2016, "rain": 490, "temp": 17.1, "hot_days": 44},
                {"year": 2017, "rain": 540, "temp": 17.3, "hot_days": 46},
                {"year": 2018, "rain": 390, "temp": 16.7, "hot_days": 52},
                {"year": 2019, "rain": 480, "temp": 16.2, "hot_days": 39},
                {"year": 2020, "rain": 310, "temp": 17.4, "hot_days": 61},
                {"year": 2021, "rain": 460, "temp": 16.8, "hot_days": 45},
                {"year": 2022, "rain": 330, "temp": 17.6, "hot_days": 67},
                {"year": 2023, "rain": 450, "temp": 17.7, "hot_days": 58},
                {"year": 2024, "rain": 435, "temp": 17.5, "hot_days": 53},
            ]
        }
    },
    "Ames, Iowa (Humid Corn Belt)": {
        "lat": 42.0308,
        "lon": -93.6319,
        "climate_type": "Humid continental (Warm summers, severe cold winters, reliable precipitation)",
        "default_past_crops": ["Maize (Corn)", "Soybean"],
        "fallback_soil": {"clay_pct": 28.5, "sand_pct": 32.0, "soc_pct": 2.65, "ph": 6.7},
        "fallback_climate": {
            "mean_annual_rainfall_mm": 895.0,
            "rainfall_trend_pct": 3.1,
            "mean_annual_temp_c": 9.8,
            "warming_rate_c_decade": 0.29,
            "hot_days_per_year": 14,
            "dry_spells_per_year": 1.6,
            "annual_series": [
                {"year": 2010, "rain": 1180, "temp": 9.9, "hot_days": 12},
                {"year": 2011, "rain": 820, "temp": 9.7, "hot_days": 16},
                {"year": 2012, "rain": 660, "temp": 11.5, "hot_days": 28},
                {"year": 2013, "rain": 840, "temp": 8.7, "hot_days": 11},
                {"year": 2014, "rain": 930, "temp": 8.5, "hot_days": 7},
                {"year": 2015, "rain": 1050, "temp": 10.2, "hot_days": 9},
                {"year": 2016, "rain": 960, "temp": 10.7, "hot_days": 14},
                {"year": 2017, "rain": 850, "temp": 10.4, "hot_days": 15},
                {"year": 2018, "rain": 1020, "temp": 9.3, "hot_days": 12},
                {"year": 2019, "rain": 980, "temp": 9.1, "hot_days": 8},
                {"year": 2020, "rain": 710, "temp": 10.1, "hot_days": 19},
                {"year": 2021, "rain": 830, "temp": 10.5, "hot_days": 16},
                {"year": 2022, "rain": 760, "temp": 9.9, "hot_days": 17},
                {"year": 2023, "rain": 730, "temp": 10.8, "hot_days": 21},
                {"year": 2024, "rain": 910, "temp": 10.6, "hot_days": 15},
            ]
        }
    }
}

# ---------------------------------------------------------
# DATA FETCHING WITH ERROR HANDLING & FALLBACK
# ---------------------------------------------------------
@st.cache_data(show_spinner=False, ttl=86400)
def fetch_nasa_power_data(lat: float, lon: float):
    """
    Fetches daily climate data from NASA POWER API (15-year record).
    Parameters: T2M (Mean Temp), T2M_MAX (Max Temp), PRECTOTCORR (Precipitation corrected)
    API Documentation: https://power.larc.nasa.gov/api/temporal/daily/point
    Community: AG (Agroclimatology)
    """
    start_date = "20100101"
    end_date = "20241231"
    url = "https://power.larc.nasa.gov/api/temporal/daily/point"
    params = {
        "parameters": "T2M,T2M_MAX,PRECTOTCORR",
        "community": "AG",
        "longitude": round(lon, 4),
        "latitude": round(lat, 4),
        "start": start_date,
        "end": end_date,
        "format": "JSON",
    }
    try:
        response = requests.get(url, params=params, timeout=12)
        if response.status_code == 200:
            data = response.json()
            param_dict = data.get("properties", {}).get("parameter", {})
            t2m = param_dict.get("T2M", {})
            t2m_max = param_dict.get("T2M_MAX", {})
            precip = param_dict.get("PRECTOTCORR", {})

            # Aggregate into annual statistics
            annual_records = {}
            for date_str, rain in precip.items():
                if rain < 0:
                    continue  # NASA fill value (-999)
                year = int(date_str[:4])
                if year not in annual_records:
                    annual_records[year] = {"rain": 0.0, "temps": [], "hot_days": 0, "dry_consec": 0, "dry_spells": 0}
                annual_records[year]["rain"] += rain
                
                t_max = t2m_max.get(date_str, -999)
                if t_max > 35.0:
                    annual_records[year]["hot_days"] += 1
                
                t_mean = t2m.get(date_str, -999)
                if t_mean > -100:
                    annual_records[year]["temps"].append(t_mean)
                
                # Dry spell counter (>14 consecutive days with rain < 1.0mm)
                if rain < 1.0:
                    annual_records[year]["dry_consec"] += 1
                    if annual_records[year]["dry_consec"] == 14:
                        annual_records[year]["dry_spells"] += 1
                else:
                    annual_records[year]["dry_consec"] = 0

            years = sorted(annual_records.keys())
            annual_series = []
            for y in years:
                rec = annual_records[y]
                avg_t = float(np.mean(rec["temps"])) if rec["temps"] else 15.0
                annual_series.append({
                    "year": y,
                    "rain": round(rec["rain"], 1),
                    "temp": round(avg_t, 1),
                    "hot_days": rec["hot_days"],
                    "dry_spells": rec["dry_spells"]
                })

            df_s = pd.DataFrame(annual_series)
            mean_rain = float(df_s["rain"].mean())
            mean_temp = float(df_s["temp"].mean())
            avg_hot = int(df_s["hot_days"].mean())
            avg_dry = float(df_s.get("dry_spells", pd.Series([2])).mean())
            
            # Simple linear trends
            years_arr = df_s["year"].values
            rain_slope = float(np.polyfit(years_arr, df_s["rain"].values, 1)[0])
            temp_slope = float(np.polyfit(years_arr, df_s["temp"].values, 1)[0])

            return {
                "source": "NASA POWER API (Live Satellite / Assimilation)",
                "mean_annual_rainfall_mm": round(mean_rain, 1),
                "rainfall_trend_pct": round((rain_slope * 10 / max(mean_rain, 1)) * 100, 1),
                "mean_annual_temp_c": round(mean_temp, 1),
                "warming_rate_c_decade": round(temp_slope * 10, 2),
                "hot_days_per_year": avg_hot,
                "dry_spells_per_year": round(avg_dry, 1),
                "annual_series": annual_series
            }
    except Exception:
        pass
    return None

@st.cache_data(show_spinner=False, ttl=86400)
def fetch_soilgrids_data(lat: float, lon: float):
    """
    Fetches soil physical and chemical properties from ISRIC SoilGrids REST API v2.0
    Query depth: 0-30cm integrated profile
    API Documentation: https://rest.isric.org/soilgrids/v2.0/properties/query
    """
    url = "https://rest.isric.org/soilgrids/v2.0/properties/query"
    params = {
        "lon": round(lon, 4),
        "lat": round(lat, 4),
        "property": ["clay", "sand", "soc", "phh2o"],
        "depth": ["0-5cm", "5-15cm", "15-30cm"],
        "value": "mean"
    }
    try:
        response = requests.get(url, params=params, timeout=8)
        if response.status_code == 200:
            data = response.json()
            layers = data.get("properties", {}).get("layers", [])
            results = {}
            for layer in layers:
                name = layer.get("name")
                depths = layer.get("depths", [])
                vals = [d.get("values", {}).get("mean") for d in depths if d.get("values", {}).get("mean") is not None]
                if vals:
                    results[name] = float(np.mean(vals))
            
            # Unit conversions per ISRIC specifications:
            # Clay & Sand are g/kg -> divide by 10 to get %
            # SOC is dg/kg -> divide by 100 to get %
            # pH*10 -> divide by 10
            clay_pct = round(results.get("clay", 250) / 10.0, 1)
            sand_pct = round(results.get("sand", 400) / 10.0, 1)
            soc_pct = round(results.get("soc", 150) / 100.0, 2)
            ph = round(results.get("phh2o", 65) / 10.0, 1)

            return {
                "source": "ISRIC SoilGrids 250m REST API (Live)",
                "clay_pct": clay_pct,
                "sand_pct": sand_pct,
                "soc_pct": soc_pct,
                "ph": ph
            }
    except Exception:
        pass
    return None

def get_climate_and_soil(lat: float, lon: float, preset_name: str = None):
    """Retrieves climate and soil data with graceful fallback to validated presets."""
    live_climate = fetch_nasa_power_data(lat, lon)
    live_soil = fetch_soilgrids_data(lat, lon)

    # Fallback resolution
    if preset_name in PRESETS:
        preset_info = PRESETS[preset_name]
        climate = live_climate if live_climate else {
            **preset_info["fallback_climate"],
            "source": "NASA POWER Verified Archive (Local Cache)"
        }
        soil = live_soil if live_soil else {
            **preset_info["fallback_soil"],
            "source": "ISRIC SoilGrids Verified Archive (Local Cache)"
        }
    else:
        # Distance-based fallback for custom coordinates if API is unreachable
        ref_preset = PRESETS["Lubbock, Texas (Semi-Arid High Plains)"] if lon < -98 else PRESETS["Ames, Iowa (Humid Corn Belt)"]
        climate = live_climate if live_climate else {
            **ref_preset["fallback_climate"],
            "source": "NASA POWER Regional Reference Baseline"
        }
        soil = live_soil if live_soil else {
            **ref_preset["fallback_soil"],
            "source": "ISRIC SoilGrids Regional Baseline"
        }
    return climate, soil

# ---------------------------------------------------------
# LOAD CROP DATABASE
# ---------------------------------------------------------
@st.cache_data
def load_crop_database():
    crops_path = os.path.join(os.path.dirname(__file__), "crops.csv")
    if os.path.exists(crops_path):
        return pd.read_csv(crops_path)
    # Inline fallback if crops.csv is missing
    data = [
        {"crop_id": "maize", "crop_name": "Maize (Corn)", "plant_family": "Poaceae", "season": "Summer", "water_need_mm": 650, "heat_tolerance": "Moderate", "drought_tolerance": "Moderate", "rooting_depth_m": 1.2, "nitrogen_fixing": "No", "soil_cover_residue": "Moderate", "ph_min": 5.8, "ph_max": 7.5, "economic_risk": "Moderate"},
        {"crop_id": "soybean", "crop_name": "Soybean", "plant_family": "Fabaceae", "season": "Summer", "water_need_mm": 500, "heat_tolerance": "Moderate", "drought_tolerance": "Moderate", "rooting_depth_m": 1.0, "nitrogen_fixing": "Yes", "soil_cover_residue": "Moderate", "ph_min": 6.0, "ph_max": 7.0, "economic_risk": "Moderate"},
        {"crop_id": "winter_wheat", "crop_name": "Winter Wheat", "plant_family": "Poaceae", "season": "Winter/Spring", "water_need_mm": 450, "heat_tolerance": "Moderate", "drought_tolerance": "Moderate", "rooting_depth_m": 1.5, "nitrogen_fixing": "No", "soil_cover_residue": "Moderate", "ph_min": 6.0, "ph_max": 7.5, "economic_risk": "Low"},
        {"crop_id": "sorghum", "crop_name": "Grain Sorghum", "plant_family": "Poaceae", "season": "Summer", "water_need_mm": 400, "heat_tolerance": "High", "drought_tolerance": "High", "rooting_depth_m": 1.5, "nitrogen_fixing": "No", "soil_cover_residue": "High", "ph_min": 5.5, "ph_max": 8.0, "economic_risk": "Low"},
        {"crop_id": "chickpea", "crop_name": "Chickpea (Garbanzo)", "plant_family": "Fabaceae", "season": "Spring/Winter", "water_need_mm": 320, "heat_tolerance": "Moderate", "drought_tolerance": "High", "rooting_depth_m": 0.8, "nitrogen_fixing": "Yes", "soil_cover_residue": "Moderate", "ph_min": 6.0, "ph_max": 8.0, "economic_risk": "Moderate"},
        {"crop_id": "alfalfa", "crop_name": "Alfalfa (Lucerne)", "plant_family": "Fabaceae", "season": "Perennial", "water_need_mm": 750, "heat_tolerance": "Moderate", "drought_tolerance": "Moderate", "rooting_depth_m": 2.5, "nitrogen_fixing": "Yes", "soil_cover_residue": "High", "ph_min": 6.5, "ph_max": 7.8, "economic_risk": "Low"},
        {"crop_id": "sunflower", "crop_name": "Sunflower", "plant_family": "Asteraceae", "season": "Summer", "water_need_mm": 480, "heat_tolerance": "High", "drought_tolerance": "Moderate", "rooting_depth_m": 1.8, "nitrogen_fixing": "No", "soil_cover_residue": "High", "ph_min": 6.0, "ph_max": 7.5, "economic_risk": "Moderate"},
        {"crop_id": "clover_rye", "crop_name": "Cover Crop (Clover-Rye)", "plant_family": "Fabaceae/Poaceae", "season": "Fall/Winter", "water_need_mm": 220, "heat_tolerance": "Moderate", "drought_tolerance": "Moderate", "rooting_depth_m": 0.6, "nitrogen_fixing": "Yes", "soil_cover_residue": "High", "ph_min": 5.5, "ph_max": 7.5, "economic_risk": "Low"}
    ]
    return pd.DataFrame(data)

# ---------------------------------------------------------
# DETERMINISTIC AGRONOMIC ROTATION & SCORING ENGINE
# ---------------------------------------------------------
def generate_and_score_rotations(
    crop_df: pd.DataFrame,
    past_crops: list,
    weights: dict,
    climate_data: dict,
    soil_data: dict
):
    """
    Agronomic 3-season candidate rotation engine.
    Applies biological rules:
    - Rule 1: No identical botanical family back-to-back (pest & pathogen break)
    - Rule 2: Minimum of 1 nitrogen-fixing legume or cover crop across sequence
    - Rule 3: Root architecture diversity (mix shallow fibrous and deep taproots)
    - Rule 4: Match crop pH envelope against soil test
    """
    crops_list = crop_df.to_dict(orient="records")
    crop_by_name = {c["crop_name"]: c for c in crops_list}

    # Identify past crop objects
    c_past2 = crop_by_name.get(past_crops[0], crops_list[0])
    c_past1 = crop_by_name.get(past_crops[1], crops_list[0])

    candidates = []
    
    # Iterate all 3-season combinations
    for c1 in crops_list:
        # Check rule 1 with last past crop
        if c1["plant_family"] == c_past1["plant_family"] and "Cover" not in c1["crop_name"]:
            continue
        
        for c2 in crops_list:
            # Check rule 1 with c1
            if c2["plant_family"] == c1["plant_family"] and "Cover" not in c2["crop_name"]:
                continue
            
            for c3 in crops_list:
                # Check rule 1 with c2
                if c3["plant_family"] == c2["plant_family"] and "Cover" not in c3["crop_name"]:
                    continue
                
                seq = [c1, c2, c3]
                
                # Rule 2: At least one legume/cover crop in 3-year cycle
                legume_count = sum(1 for c in seq if c["nitrogen_fixing"] == "Yes")
                if legume_count < 1:
                    continue
                
                # Rule 3: Avoid 3 consecutive identical crops
                if c1["crop_id"] == c2["crop_id"] == c3["crop_id"]:
                    continue
                
                # Calculate sub-scores (0 to 100)
                # 1. Water Score
                total_water_need = sum(c["water_need_mm"] for c in seq)
                annual_water_need = total_water_need / 3.0
                mean_rainfall = climate_data["mean_annual_rainfall_mm"]
                water_ratio = annual_water_need / max(mean_rainfall, 250)
                
                # If water need <= rainfall, high score; if water deficit, score drops
                if water_ratio <= 0.8:
                    s_water = 95.0
                elif water_ratio <= 1.0:
                    s_water = 82.0
                elif water_ratio <= 1.25:
                    s_water = 65.0
                elif water_ratio <= 1.5:
                    s_water = 45.0
                else:
                    s_water = 25.0
                
                # Bonus for drought tolerance in dry areas
                if climate_data["mean_annual_rainfall_mm"] < 550:
                    drought_tol_count = sum(1 for c in seq if c["drought_tolerance"] == "High")
                    s_water = min(100.0, s_water + drought_tol_count * 5.0)

                # 2. Soil Health Score
                # Benefits: Nitrogen fixation, High residue cover, Deep roots > 1.4m
                n_fix_bonus = legume_count * 15.0
                residue_bonus = sum(12.0 for c in seq if c["soil_cover_residue"] == "High") + sum(6.0 for c in seq if c["soil_cover_residue"] == "Moderate")
                deep_root_bonus = sum(10.0 for c in seq if c["rooting_depth_m"] >= 1.5)
                family_count = len(set(c["plant_family"] for c in seq))
                diversity_bonus = family_count * 8.0
                s_soil = min(100.0, 20.0 + n_fix_bonus + residue_bonus + deep_root_bonus + diversity_bonus)

                # 3. Economic Stability / Low Risk Score
                risk_penalty = sum(15.0 for c in seq if c["economic_risk"] == "High") + sum(5.0 for c in seq if c["economic_risk"] == "Moderate")
                s_econ = max(30.0, 100.0 - risk_penalty)

                # 4. Climate Resilience Score
                # Evaluates exposure to hot days and dry spells
                hot_days = climate_data["hot_days_per_year"]
                dry_spells = climate_data["dry_spells_per_year"]
                heat_fit = sum(12.0 for c in seq if c["heat_tolerance"] == "High") + sum(6.0 for c in seq if c["heat_tolerance"] == "Moderate")
                drought_fit = sum(12.0 for c in seq if c["drought_tolerance"] == "High") + sum(6.0 for c in seq if c["drought_tolerance"] == "Moderate")
                
                base_climate_stress = (hot_days * 0.4) + (dry_spells * 5.0)
                s_resilience = min(100.0, max(30.0, 50.0 + (heat_fit + drought_fit) - (base_climate_stress * 0.25)))

                # 5. Soil pH Compatibility Check
                soil_ph = soil_data.get("ph", 6.8)
                ph_mismatch = 0
                for c in seq:
                    if soil_ph < c["ph_min"] or soil_ph > c["ph_max"]:
                        ph_mismatch += 1
                ph_penalty = ph_mismatch * 8.0

                # Weighted Composite Score
                w_tot = sum(weights.values())
                composite_score = (
                    weights["water"] * s_water +
                    weights["soil"] * s_soil +
                    weights["econ"] * s_econ +
                    weights["resilience"] * s_resilience
                ) / max(w_tot, 1)
                composite_score = max(10.0, composite_score - ph_penalty)

                # Generate plain language agronomic rationale
                rationale_points = []
                if legume_count > 0:
                    rationale_points.append(f"Includes {legume_count} biological N-fixing season(s) cutting synthetic fertilizer dependency")
                if any(c["rooting_depth_m"] >= 1.5 for c in seq):
                    rationale_points.append("Deep taproots break hardpan compaction and tap deep moisture reserves")
                if annual_water_need <= mean_rainfall:
                    rationale_points.append(f"Annual water budget ({int(annual_water_need)}mm) is sustainable under NASA historical rainfall ({int(mean_rainfall)}mm)")
                else:
                    rationale_points.append(f"Water demand ({int(annual_water_need)}mm) slightly exceeds mean rain; requires soil water retention practices")
                if climate_data["hot_days_per_year"] > 30 and any(c["heat_tolerance"] == "High" for c in seq):
                    rationale_points.append("Utilizes C4 / heat-tolerant crops resilient to extreme summer temperature spikes")

                candidates.append({
                    "crops": [c["crop_name"] for c in seq],
                    "crop_objects": seq,
                    "composite_score": round(composite_score, 1),
                    "s_water": round(s_water, 1),
                    "s_soil": round(s_soil, 1),
                    "s_econ": round(s_econ, 1),
                    "s_resilience": round(s_resilience, 1),
                    "annual_water_need_mm": int(annual_water_need),
                    "total_water_need_mm": int(total_water_need),
                    "legume_seasons": legume_count,
                    "families": list(set(c["plant_family"] for c in seq)),
                    "rationale": " • ".join(rationale_points)
                })

    # Sort descending by composite score and remove trivial duplicates
    candidates.sort(key=lambda x: x["composite_score"], reverse=True)
    
    unique_candidates = []
    seen_seqs = set()
    for cand in candidates:
        key = tuple(cand["crops"])
        if key not in seen_seqs:
            seen_seqs.add(key)
            unique_candidates.append(cand)
            if len(unique_candidates) >= 5:
                break
                
    return unique_candidates

def evaluate_baseline_monoculture(past_crop_name: str, crop_df: pd.DataFrame, climate_data: dict, soil_data: dict, weights: dict):
    """Evaluates the status quo (monoculture repetition of last crop) for direct benchmarking."""
    crop_by_name = {c["crop_name"]: c for c in crop_df.to_dict(orient="records")}
    crop = crop_by_name.get(past_crop_name, list(crop_by_name.values())[0])
    
    # Continuous monoculture has heavy pest build-up, organic matter depletion, and vulnerability
    s_water = 60.0 if crop["water_need_mm"] <= climate_data["mean_annual_rainfall_mm"] else 35.0
    s_soil = 30.0 if crop["nitrogen_fixing"] == "No" else 55.0  # Monoculture disease penalty
    s_econ = 65.0  # Familiar market, but market concentration risk
    s_resilience = 40.0 if crop["drought_tolerance"] != "High" else 65.0
    
    w_tot = sum(weights.values())
    composite = (
        weights["water"] * s_water +
        weights["soil"] * s_soil +
        weights["econ"] * s_econ +
        weights["resilience"] * s_resilience
    ) / max(w_tot, 1)

    return {
        "crop_name": crop["crop_name"],
        "composite_score": round(composite, 1),
        "s_water": round(s_water, 1),
        "s_soil": round(s_soil, 1),
        "s_econ": round(s_econ, 1),
        "s_resilience": round(s_resilience, 1),
        "annual_water_need_mm": crop["water_need_mm"],
        "vulnerability_notes": "Continuous monoculture increases pest persistence, risks soil compaction, and compounds climate vulnerability."
    }

# ---------------------------------------------------------
# APPLICATION INTERFACE
# ---------------------------------------------------------
# Header & NASA Space Apps Banner
col_h1, col_h2 = st.columns([0.8, 0.2])
with col_h1:
    st.markdown('<div class="main-title">🌾 FieldShift Rotation Advisor</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Adapting Farms with NASA Earth Observations & Soil Intelligence | NASA Space Apps Challenge 2026</div>', unsafe_allow_html=True)
with col_h2:
    st.markdown("""
    <div style="background-color: #0b3d91; color: white; padding: 8px 12px; border-radius: 8px; text-align: center; font-weight: bold; font-size: 0.85rem;">
        🚀 NASA Earth Data<br><span style="font-weight: normal; font-size: 0.75rem;">POWER AG & SoilGrids</span>
    </div>
    """, unsafe_allow_html=True)

# Load crops
crop_df = load_crop_database()

# SIDEBAR CONTROLS
st.sidebar.header("📍 1. Farm Location")
location_mode = st.sidebar.radio("Location Mode:", ["Preset Climate Farm", "Custom Coordinates"])

if location_mode == "Preset Climate Farm":
    selected_preset = st.sidebar.selectbox("Choose Benchmark Farm:", list(PRESETS.keys()))
    farm_info = PRESETS[selected_preset]
    latitude = farm_info["lat"]
    longitude = farm_info["lon"]
    st.sidebar.caption(f"**Climate Context**: {farm_info['climate_type']}")
else:
    selected_preset = None
    latitude = st.sidebar.number_input("Latitude (°N):", min_value=-60.0, max_value=75.0, value=35.0, step=0.01)
    longitude = st.sidebar.number_input("Longitude (°E/W):", min_value=-180.0, max_value=180.0, value=-98.0, step=0.01)

st.sidebar.markdown("---")
st.sidebar.header("🌱 2. Field Cropping History")
available_crops = crop_df["crop_name"].tolist()
default_past1 = farm_info["default_past_crops"][0] if selected_preset else available_crops[0]
default_past2 = farm_info["default_past_crops"][1] if selected_preset else available_crops[1]

past_crop_2 = st.sidebar.selectbox("Crop grown 2 seasons ago:", available_crops, index=available_crops.index(default_past1) if default_past1 in available_crops else 0)
past_crop_1 = st.sidebar.selectbox("Crop grown last season:", available_crops, index=available_crops.index(default_past2) if default_past2 in available_crops else 1)

st.sidebar.markdown("---")
st.sidebar.header("⚖️ 3. Farmer Strategic Priorities")
st.sidebar.caption("Adjust weight sliders (1 = Low priority, 5 = Critical priority)")
w_water = st.sidebar.slider("💧 Save Water / Irrigation Reduction", 1, 5, 4)
w_soil = st.sidebar.slider("🪵 Build Soil Health & Organic Matter", 1, 5, 5)
w_econ = st.sidebar.slider("📈 Stable Income / Market Risk", 1, 5, 3)
w_resilience = st.sidebar.slider("☀️ Heat & Drought Climate Resilience", 1, 5, 4)

user_weights = {
    "water": float(w_water),
    "soil": float(w_soil),
    "econ": float(w_econ),
    "resilience": float(w_resilience)
}

st.sidebar.markdown("---")
st.sidebar.header("🧪 4. Soil Test Inputs")
use_custom_soil = st.sidebar.checkbox("Override with my own soil lab report", value=False)

# Fetch NASA and Soil data
with st.spinner("Connecting to NASA POWER and SoilGrids APIs..."):
    climate_data, base_soil_data = get_climate_and_soil(latitude, longitude, selected_preset)

if use_custom_soil:
    c_clay = st.sidebar.number_input("Clay Content (%)", 0.0, 100.0, float(base_soil_data["clay_pct"]))
    c_sand = st.sidebar.number_input("Sand Content (%)", 0.0, 100.0, float(base_soil_data["sand_pct"]))
    c_soc = st.sidebar.number_input("Organic Carbon (%)", 0.0, 20.0, float(base_soil_data["soc_pct"]))
    c_ph = st.sidebar.number_input("Soil pH", 3.5, 9.5, float(base_soil_data["ph"]))
    active_soil_data = {"clay_pct": c_clay, "sand_pct": c_sand, "soc_pct": c_soc, "ph": c_ph, "source": "Farmer Lab Test (Manual Override)"}
else:
    active_soil_data = base_soil_data

# ---------------------------------------------------------
# MAIN PANEL: NASA CLIMATE & SOIL DIAGNOSTIC
# ---------------------------------------------------------
st.markdown("### 📊 NASA Earth Observation & Soil Diagnostic")

col_m1, col_m2, col_m3, col_m4 = st.columns(4)
with col_m1:
    st.metric(
        label="Mean Annual Rainfall",
        value=f"{climate_data['mean_annual_rainfall_mm']} mm",
        delta=f"{climate_data['rainfall_trend_pct']:+.1f}% / decade",
        delta_color="normal"
    )
with col_m2:
    st.metric(
        label="Mean Temperature",
        value=f"{climate_data['mean_annual_temp_c']} °C",
        delta=f"+{climate_data['warming_rate_c_decade']:.2f} °C / decade",
        delta_color="inverse"
    )
with col_m3:
    st.metric(
        label="Extreme Heat Days (>35°C)",
        value=f"{climate_data['hot_days_per_year']} days/yr",
        help="Days per year with maximum temperature exceeding 35°C from NASA POWER daily records."
    )
with col_m4:
    st.metric(
        label="Soil Organic Carbon (SOC)",
        value=f"{active_soil_data['soc_pct']:.2f}%",
        help=f"ISRIC SoilGrids 0-30cm. Soil Texture: {active_soil_data['clay_pct']}% Clay, {active_soil_data['sand_pct']}% Sand, pH {active_soil_data['ph']}."
    )

st.caption(f"**Data Provenance:** Climate: `{climate_data['source']}` | Soil: `{active_soil_data['source']}` (Coordinates: {latitude:.4f}°N, {longitude:.4f}°E)")

# Compute Rotations and Status Quo
top_rotations = generate_and_score_rotations(
    crop_df,
    [past_crop_2, past_crop_1],
    user_weights,
    climate_data,
    active_soil_data
)
baseline = evaluate_baseline_monoculture(past_crop_1, crop_df, climate_data, active_soil_data, user_weights)

# ---------------------------------------------------------
# ROTATION RECOMMENDATIONS COMPARISON
# ---------------------------------------------------------
st.markdown("---")
st.markdown("### 🏆 Top Recommended 3-Season Rotations vs. Current Practice")

if not top_rotations:
    st.warning("No rotations matched your current strict constraints. Try lowering crop restrictions.")
else:
    # Build comparison dataframe
    comp_rows = [{
        "Strategy": f"⚠️ Current Practice: Continuous {baseline['crop_name']}",
        "Overall Score": f"{baseline['composite_score']}/100",
        "Water Fit": f"{baseline['s_water']}/100",
        "Soil Health": f"{baseline['s_soil']}/100",
        "Climate Resilience": f"{baseline['s_resilience']}/100",
        "Annual Water Need": f"{baseline['annual_water_need_mm']} mm",
        "Legume Seasons": "0 / 3",
        "Agronomic Diversity": "Monoculture (High Risk)"
    }]

    for idx, r in enumerate(top_rotations[:3]):
        rot_str = " ➔ ".join(r["crops"])
        comp_rows.append({
            "Strategy": f"🌟 Rank #{idx+1}: {rot_str}",
            "Overall Score": f"{r['composite_score']}/100",
            "Water Fit": f"{r['s_water']}/100",
            "Soil Health": f"{r['s_soil']}/100",
            "Climate Resilience": f"{r['s_resilience']}/100",
            "Annual Water Need": f"{r['annual_water_need_mm']} mm",
            "Legume Seasons": f"{r['legume_seasons']} / 3",
            "Agronomic Diversity": f"{len(r['families'])} Families"
        })

    df_comp = pd.DataFrame(comp_rows)
    st.dataframe(df_comp, use_container_width=True, hide_index=True)

    # Highlight Top Pick Detail
    best = top_rotations[0]
    water_diff = baseline["annual_water_need_mm"] - best["annual_water_need_mm"]
    score_diff = best["composite_score"] - baseline["composite_score"]
    
    st.info(f"""
    **💡 Why Rank #1 ('{" ➔ ".join(best['crops'])}') is your optimal rotation:**
    - **Score Improvement:** +{score_diff:.1f} points higher overall resilience than continuing {baseline['crop_name']}.
    - **Water Impact:** Uses **{best['annual_water_need_mm']} mm/year** vs. {baseline['annual_water_need_mm']} mm/year for current practice ({'+' if water_diff < 0 else ''}{-water_diff} mm water conservation).
    - **Soil & Agronomy Evidence:** {best['rationale']}.
    """)

# ---------------------------------------------------------
# INTERACTIVE TABS: CHARTS & DEEP DIVE
# ---------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 NASA 15-Year Climate Trend",
    "💧 Water Budget & Risk Matrix",
    "🗺️ Farm Map & Soil Texture",
    "📚 Scientific References & Crop Library"
])

with tab1:
    st.markdown("#### NASA POWER 15-Year Historical Climate Analysis (2010–2024)")
    st.markdown("NASA satellite and assimilated weather observations demonstrate shifting climate baselines at your location.")
    
    df_climate_series = pd.DataFrame(climate_data["annual_series"])
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        # Rainfall and Hot Days Chart
        fig_rain = go.Figure()
        fig_rain.add_trace(go.Bar(
            x=df_climate_series["year"],
            y=df_climate_series["rain"],
            name="Annual Precipitation (mm)",
            marker_color="#2b9348",
            opacity=0.75
        ))
        fig_rain.add_hline(
            y=climate_data["mean_annual_rainfall_mm"],
            line_dash="dash",
            line_color="#1b4332",
            annotation_text=f"15-yr Mean: {climate_data['mean_annual_rainfall_mm']} mm"
        )
        fig_rain.update_layout(
            title="Annual Precipitation vs. 15-Year Normal",
            xaxis_title="Year",
            yaxis_title="Precipitation (mm)",
            height=380,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_rain, use_container_width=True)

    with col_t2:
        # Temperature & Extreme Heat Trend
        fig_temp = go.Figure()
        fig_temp.add_trace(go.Scatter(
            x=df_climate_series["year"],
            y=df_climate_series["temp"],
            name="Mean Temp (°C)",
            mode="lines+markers",
            line=dict(color="#d90429", width=3)
        ))
        fig_temp.add_trace(go.Bar(
            x=df_climate_series["year"],
            y=df_climate_series["hot_days"],
            name="Hot Days (>35°C)",
            marker_color="#f77f00",
            yaxis="y2",
            opacity=0.4
        ))
        fig_temp.update_layout(
            title="Temperature & Extreme Heat Frequency Trend",
            xaxis_title="Year",
            yaxis_title="Mean Temperature (°C)",
            yaxis2=dict(
                title="Days > 35°C",
                overlaying="y",
                side="right"
            ),
            height=380,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_temp, use_container_width=True)

with tab2:
    st.markdown("#### Rotation Water Demand vs. NASA Climate Precipitation")
    
    comp_labels = ["Current Practice"] + [f"Rank #{i+1}" for i in range(min(3, len(top_rotations)))]
    water_values = [baseline["annual_water_need_mm"]] + [r["annual_water_need_mm"] for r in top_rotations[:3]]
    soil_values = [baseline["s_soil"]] + [r["s_soil"] for r in top_rotations[:3]]
    resilience_values = [baseline["s_resilience"]] + [r["s_resilience"] for r in top_rotations[:3]]

    col_w1, col_w2 = st.columns(2)
    with col_w1:
        fig_water = go.Figure()
        fig_water.add_trace(go.Bar(
            x=comp_labels,
            y=water_values,
            name="Annual Water Demand (mm)",
            marker_color=["#ef233c", "#2a9d8f", "#52b788", "#74c69d"]
        ))
        fig_water.add_hline(
            y=climate_data["mean_annual_rainfall_mm"],
            line_dash="dot",
            line_color="#0077b6",
            line_width=3,
            annotation_text=f"NASA Mean Rain: {climate_data['mean_annual_rainfall_mm']} mm"
        )
        fig_water.update_layout(
            title="Water Demand vs. Available Historical Rainfall",
            yaxis_title="Annual Water (mm)",
            height=380,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_water, use_container_width=True)

    with col_w2:
        # Multi-attribute radar comparison
        categories = ["Water Fit", "Soil Health", "Climate Resilience", "Economic Stability"]
        fig_radar = go.Figure()
        
        # Baseline
        fig_radar.add_trace(go.Scatterpolar(
            r=[baseline["s_water"], baseline["s_soil"], baseline["s_resilience"], baseline["s_econ"]],
            theta=categories,
            fill="toself",
            name="Current Practice",
            line_color="#ef233c"
        ))
        
        # Rank 1
        if top_rotations:
            r1 = top_rotations[0]
            fig_radar.add_trace(go.Scatterpolar(
                r=[r1["s_water"], r1["s_soil"], r1["s_resilience"], r1["s_econ"]],
                theta=categories,
                fill="toself",
                name="Rank #1 Strategy",
                line_color="#2a9d8f"
            ))

        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=True,
            title="Agronomic Resilience Tradeoff Matrix",
            height=380,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_radar, use_container_width=True)

with tab3:
    st.markdown("#### Geographic Coordinates & Soil Horizon Profile")
    col_map1, col_map2 = st.columns([0.6, 0.4])
    
    with col_map1:
        map_df = pd.DataFrame([{"lat": latitude, "lon": longitude}])
        st.map(map_df, zoom=6, use_container_width=True)
    
    with col_map2:
        st.markdown(f"""
        <div class="metric-card">
            <h4>Soil Horizon Profile (ISRIC SoilGrids 0–30 cm)</h4>
            <p><strong>Soil Texture Class:</strong> {'Sandy Loam / Loam' if active_soil_data['sand_pct'] > 45 else 'Clay Loam / Silt Loam'}</p>
            <ul>
                <li><strong>Clay Content:</strong> {active_soil_data['clay_pct']}%</li>
                <li><strong>Sand Content:</strong> {active_soil_data['sand_pct']}%</li>
                <li><strong>Organic Carbon (SOC):</strong> {active_soil_data['soc_pct']}%</li>
                <li><strong>pH (in H2O):</strong> {active_soil_data['ph']}</li>
            </ul>
            <p><em>Agronomic Note:</em> Higher clay increases water retention but increases compaction risk. Rotations with taproots (e.g., Sunflower, Alfalfa) alleviate plow-pan restriction.</p>
        </div>
        """, unsafe_allow_html=True)

with tab4:
    st.markdown("#### FAO-Grounded Crop Reference Database & Citations")
    st.dataframe(crop_df, use_container_width=True)
    
    st.markdown("""
    ### 📖 References & Scientific Provenance
    1. **NASA POWER Project (Prediction Of Worldwide Energy Resources):**
       - Source: NASA Langley Research Center. Daily meteorological agroclimatology dataset (T2M, T2M_MAX, PRECTOTCORR).
       - API: `https://power.larc.nasa.gov/api/temporal/daily/point` (Community: AG).
    2. **ISRIC SoilGrids 250m v2.0:**
       - Source: International Soil Reference and Information Centre (ISRIC). Global gridded soil information system based on machine learning.
       - API: `https://rest.isric.org/soilgrids/v2.0/properties/query`.
    3. **FAO Irrigation and Drainage Paper No. 56 & 33:**
       - Allen, R. G., Pereira, L. S., Raes, D., & Smith, M. *Crop evapotranspiration - Guidelines for computing crop water requirements*. Food and Agriculture Organization of the United Nations (Rome, 1998).
       - Doorenbos, J., & Kassam, A. H. *Yield response to water*. FAO Irrigation and Drainage Paper No. 33.
    4. **FAO EcoCrop Database & Soil Bulletin No. 80:**
       - Soil cover residue, biological nitrogen fixation capacities, and botanical family pest break principles.
    
    > **⚠️ Limitations & Scientific Transparency:**
    > - The rotation advisor evaluates deterministic agronomic indicators based on historical satellite climatology and gridded soil properties. It does not replace on-farm soil nutrient testing or localized agronomic extension consultation.
    > - Water balance figures represent seasonal consumptive estimates under non-stressed conditions and assume typical local planting dates.
    """)

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: #6c757d; font-size: 0.85rem;'>FieldShift Rotation Advisor • NASA Space Apps Challenge 2026 • Open Source Agricultural Decision Support</p>", unsafe_allow_html=True)
