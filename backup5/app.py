import os
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import requests

# ---------------------------------------------------------
# PAGE CONFIGURATION & THEME INJECTION
# ---------------------------------------------------------
st.set_page_config(
    page_title="FieldShift Tactical Command | NASA Space Apps 2026",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------
# UNIVERSAL HTML RENDERING HELPER (PREVENTS CODE BLOCKS)
# ---------------------------------------------------------
def render_html(html_str: str, sidebar: bool = False):
    """
    Strips all leading/trailing indentation and empty lines, collapsing HTML
    into clean unindented text so Markdown never misinterprets it as a code block.
    Uses st.html if supported, falling back to st.markdown.
    """
    clean_lines = [line.strip() for line in html_str.splitlines() if line.strip()]
    cleaned = "\n".join(clean_lines)
    target = st.sidebar if sidebar else st
    if hasattr(target, "html"):
        target.html(cleaned)
    else:
        target.markdown(cleaned, unsafe_allow_html=True)

# Inject External Google Fonts & styles.css
styles_path = os.path.join(os.path.dirname(__file__), "styles.css")
if os.path.exists(styles_path):
    with open(styles_path, "r", encoding="utf-8") as f:
        render_html(f"<style>{f.read()}</style>")

# ---------------------------------------------------------
# GLOBAL BENCHMARK FARMS (7 REPRESENTATIVE AGRO-ECOLOGICAL ZONES)
# ---------------------------------------------------------
PRESETS = {
    "Lubbock, Texas, USA (Semi-Arid High Plains)": {
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
    "Ames, Iowa, USA (Humid Corn Belt)": {
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
    },
    "Ludhiana, Punjab, India (Indo-Gangetic Plain)": {
        "lat": 30.9010,
        "lon": 75.8573,
        "climate_type": "Subtropical monsoon (Intense summer monsoon, warm dry winter, groundwater stress)",
        "default_past_crops": ["Winter Wheat", "Maize (Corn)"],
        "fallback_soil": {"clay_pct": 18.0, "sand_pct": 65.0, "soc_pct": 0.45, "ph": 8.1},
        "fallback_climate": {
            "mean_annual_rainfall_mm": 680.0,
            "rainfall_trend_pct": -6.5,
            "mean_annual_temp_c": 24.2,
            "warming_rate_c_decade": 0.32,
            "hot_days_per_year": 92,
            "dry_spells_per_year": 3.8,
            "annual_series": [
                {"year": 2010, "rain": 740, "temp": 23.8, "hot_days": 88},
                {"year": 2011, "rain": 690, "temp": 24.0, "hot_days": 90},
                {"year": 2012, "rain": 580, "temp": 24.5, "hot_days": 95},
                {"year": 2013, "rain": 720, "temp": 24.1, "hot_days": 89},
                {"year": 2014, "rain": 610, "temp": 24.3, "hot_days": 93},
                {"year": 2015, "rain": 650, "temp": 24.2, "hot_days": 91},
                {"year": 2016, "rain": 590, "temp": 24.7, "hot_days": 98},
                {"year": 2017, "rain": 700, "temp": 24.4, "hot_days": 92},
                {"year": 2018, "rain": 670, "temp": 24.1, "hot_days": 90},
                {"year": 2019, "rain": 750, "temp": 23.9, "hot_days": 87},
                {"year": 2020, "rain": 630, "temp": 24.3, "hot_days": 94},
                {"year": 2021, "rain": 680, "temp": 24.5, "hot_days": 93},
                {"year": 2022, "rain": 560, "temp": 25.1, "hot_days": 104},
                {"year": 2023, "rain": 730, "temp": 24.6, "hot_days": 91},
                {"year": 2024, "rain": 640, "temp": 24.8, "hot_days": 96},
            ]
        }
    },
    "Nakuru, Rift Valley, Kenya (Equatorial Highland)": {
        "lat": -0.3031,
        "lon": 36.0800,
        "climate_type": "Highland tropical (Bimodal rainfall, mild year-round temperatures, rich volcanic soils)",
        "default_past_crops": ["Maize (Corn)", "Chickpea (Garbanzo)"],
        "fallback_soil": {"clay_pct": 32.0, "sand_pct": 28.0, "soc_pct": 2.10, "ph": 6.2},
        "fallback_climate": {
            "mean_annual_rainfall_mm": 960.0,
            "rainfall_trend_pct": -2.1,
            "mean_annual_temp_c": 17.8,
            "warming_rate_c_decade": 0.22,
            "hot_days_per_year": 4,
            "dry_spells_per_year": 2.4,
            "annual_series": [
                {"year": 2010, "rain": 1050, "temp": 17.6, "hot_days": 3},
                {"year": 2011, "rain": 890, "temp": 17.9, "hot_days": 5},
                {"year": 2012, "rain": 980, "temp": 17.7, "hot_days": 4},
                {"year": 2013, "rain": 940, "temp": 17.8, "hot_days": 4},
                {"year": 2014, "rain": 920, "temp": 17.8, "hot_days": 4},
                {"year": 2015, "rain": 1080, "temp": 17.7, "hot_days": 3},
                {"year": 2016, "rain": 910, "temp": 18.0, "hot_days": 6},
                {"year": 2017, "rain": 870, "temp": 18.1, "hot_days": 7},
                {"year": 2018, "rain": 1120, "temp": 17.6, "hot_days": 2},
                {"year": 2019, "rain": 1090, "temp": 17.8, "hot_days": 4},
                {"year": 2020, "rain": 950, "temp": 17.9, "hot_days": 5},
                {"year": 2021, "rain": 880, "temp": 18.2, "hot_days": 6},
                {"year": 2022, "rain": 840, "temp": 18.3, "hot_days": 8},
                {"year": 2023, "rain": 1010, "temp": 18.0, "hot_days": 4},
                {"year": 2024, "rain": 970, "temp": 18.1, "hot_days": 5},
            ]
        }
    },
    "Sorriso, Mato Grosso, Brazil (Cerrado Savanna)": {
        "lat": -12.5448,
        "lon": -55.7226,
        "climate_type": "Tropical wet-and-dry (Intense summer monsoon Oct-Apr, 5-month extreme winter dry season)",
        "default_past_crops": ["Soybean", "Maize (Corn)"],
        "fallback_soil": {"clay_pct": 48.0, "sand_pct": 38.0, "soc_pct": 1.45, "ph": 5.4},
        "fallback_climate": {
            "mean_annual_rainfall_mm": 1850.0,
            "rainfall_trend_pct": -3.8,
            "mean_annual_temp_c": 26.1,
            "warming_rate_c_decade": 0.41,
            "hot_days_per_year": 115,
            "dry_spells_per_year": 4.5,
            "annual_series": [
                {"year": 2010, "rain": 1920, "temp": 25.8, "hot_days": 108},
                {"year": 2011, "rain": 1880, "temp": 25.9, "hot_days": 110},
                {"year": 2012, "rain": 1790, "temp": 26.2, "hot_days": 118},
                {"year": 2013, "rain": 1940, "temp": 26.0, "hot_days": 112},
                {"year": 2014, "rain": 1810, "temp": 26.1, "hot_days": 116},
                {"year": 2015, "rain": 1720, "temp": 26.5, "hot_days": 124},
                {"year": 2016, "rain": 1760, "temp": 26.4, "hot_days": 122},
                {"year": 2017, "rain": 1890, "temp": 26.1, "hot_days": 114},
                {"year": 2018, "rain": 1950, "temp": 25.9, "hot_days": 109},
                {"year": 2019, "rain": 1820, "temp": 26.3, "hot_days": 119},
                {"year": 2020, "rain": 1690, "temp": 26.7, "hot_days": 128},
                {"year": 2021, "rain": 1840, "temp": 26.2, "hot_days": 115},
                {"year": 2022, "rain": 1780, "temp": 26.6, "hot_days": 125},
                {"year": 2023, "rain": 1860, "temp": 26.5, "hot_days": 121},
                {"year": 2024, "rain": 1800, "temp": 26.8, "hot_days": 126},
            ]
        }
    },
    "Poltava, Ukraine (Eurasian Chernozem Steppe)": {
        "lat": 49.5883,
        "lon": 34.5514,
        "climate_type": "Temperate continental (Deep black chernozem, moderate precipitation, cold winter)",
        "default_past_crops": ["Winter Wheat", "Sunflower"],
        "fallback_soil": {"clay_pct": 34.0, "sand_pct": 22.0, "soc_pct": 3.40, "ph": 6.8},
        "fallback_climate": {
            "mean_annual_rainfall_mm": 560.0,
            "rainfall_trend_pct": 1.8,
            "mean_annual_temp_c": 8.9,
            "warming_rate_c_decade": 0.48,
            "hot_days_per_year": 22,
            "dry_spells_per_year": 2.1,
            "annual_series": [
                {"year": 2010, "rain": 580, "temp": 9.1, "hot_days": 26},
                {"year": 2011, "rain": 530, "temp": 8.6, "hot_days": 18},
                {"year": 2012, "rain": 550, "temp": 9.2, "hot_days": 24},
                {"year": 2013, "rain": 610, "temp": 8.7, "hot_days": 17},
                {"year": 2014, "rain": 520, "temp": 8.9, "hot_days": 20},
                {"year": 2015, "rain": 490, "temp": 9.4, "hot_days": 28},
                {"year": 2016, "rain": 590, "temp": 9.0, "hot_days": 21},
                {"year": 2017, "rain": 540, "temp": 9.1, "hot_days": 23},
                {"year": 2018, "rain": 560, "temp": 9.3, "hot_days": 25},
                {"year": 2019, "rain": 570, "temp": 9.5, "hot_days": 27},
                {"year": 2020, "rain": 510, "temp": 9.7, "hot_days": 30},
                {"year": 2021, "rain": 580, "temp": 8.8, "hot_days": 19},
                {"year": 2022, "rain": 550, "temp": 9.2, "hot_days": 22},
                {"year": 2023, "rain": 600, "temp": 9.6, "hot_days": 26},
                {"year": 2024, "rain": 540, "temp": 9.8, "hot_days": 29},
            ]
        }
    },
    "Dubbo, New South Wales, Australia (Murray-Darling)": {
        "lat": -32.2569,
        "lon": 148.6011,
        "climate_type": "Semi-arid transitional (Highly variable rainfall, hot summer peaks, high evaporation)",
        "default_past_crops": ["Winter Wheat", "Grain Sorghum"],
        "fallback_soil": {"clay_pct": 26.0, "sand_pct": 48.0, "soc_pct": 0.95, "ph": 6.4},
        "fallback_climate": {
            "mean_annual_rainfall_mm": 580.0,
            "rainfall_trend_pct": -5.4,
            "mean_annual_temp_c": 17.9,
            "warming_rate_c_decade": 0.35,
            "hot_days_per_year": 54,
            "dry_spells_per_year": 3.5,
            "annual_series": [
                {"year": 2010, "rain": 820, "temp": 17.4, "hot_days": 46},
                {"year": 2011, "rain": 710, "temp": 17.5, "hot_days": 48},
                {"year": 2012, "rain": 620, "temp": 17.8, "hot_days": 52},
                {"year": 2013, "rain": 490, "temp": 18.2, "hot_days": 59},
                {"year": 2014, "rain": 540, "temp": 18.0, "hot_days": 56},
                {"year": 2015, "rain": 580, "temp": 17.9, "hot_days": 53},
                {"year": 2016, "rain": 760, "temp": 17.7, "hot_days": 50},
                {"year": 2017, "rain": 460, "temp": 18.3, "hot_days": 61},
                {"year": 2018, "rain": 340, "temp": 18.6, "hot_days": 68},
                {"year": 2019, "rain": 260, "temp": 18.9, "hot_days": 74},
                {"year": 2020, "rain": 690, "temp": 17.8, "hot_days": 52},
                {"year": 2021, "rain": 780, "temp": 17.5, "hot_days": 47},
                {"year": 2022, "rain": 890, "temp": 17.3, "hot_days": 44},
                {"year": 2023, "rain": 520, "temp": 18.4, "hot_days": 62},
                {"year": 2024, "rain": 560, "temp": 18.2, "hot_days": 58},
            ]
        }
    }
}

# ---------------------------------------------------------
# OCEAN & NON-FARMLAND VALIDATOR
# ---------------------------------------------------------
def check_is_farmland(lat: float, lon: float, live_soil: dict = None) -> bool:
    """
    Validates if coordinates are on continental land / arable zone, or over open ocean / polar ice.
    """
    # Polar ice sheets
    if lat > 78.0 or lat < -58.0:
        return False
        
    # Open ocean bounds
    # Pacific Ocean
    if (-55.0 <= lat <= 55.0) and (-179.9 <= lon <= -128.0):
        # Exclude Hawaii
        if not (18.0 <= lat <= 23.0 and -161.0 <= lon <= -154.0):
            return False
    if (-50.0 <= lat <= 40.0) and (155.0 <= lon <= 180.0):
        # Exclude New Zealand
        if not (-48.0 <= lat <= -34.0 and 165.0 <= lon <= 179.0):
            return False
            
    # Atlantic Ocean
    if (-45.0 <= lat <= 60.0) and (-45.0 <= lon <= -18.0):
        # Exclude Iceland
        if not (63.0 <= lat <= 67.0 and -25.0 <= lon <= -13.0):
            return False
            
    # Indian Ocean
    if (-50.0 <= lat <= 10.0) and (55.0 <= lon <= 95.0):
        if not (5.8 <= lat <= 10.0 and 79.5 <= lon <= 82.0):
            return False
            
    # If live soil data returned 0 or non-existent organic carbon
    if live_soil is not None:
        if live_soil.get("soc_pct", 0) <= 0.0:
            return False

    return True

# ---------------------------------------------------------
# DATA FETCHING (NASA POWER & ISRIC SOILGRIDS)
# ---------------------------------------------------------
@st.cache_data(show_spinner=False, ttl=86400)
def fetch_nasa_power_data(lat: float, lon: float):
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
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            param_dict = data.get("properties", {}).get("parameter", {})
            t2m = param_dict.get("T2M", {})
            t2m_max = param_dict.get("T2M_MAX", {})
            precip = param_dict.get("PRECTOTCORR", {})

            annual_records = {}
            for date_str, rain in precip.items():
                if rain < 0:
                    continue
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
    url = "https://rest.isric.org/soilgrids/v2.0/properties/query"
    params = {
        "lon": round(lon, 4),
        "lat": round(lat, 4),
        "property": ["clay", "sand", "soc", "phh2o"],
        "depth": ["0-5cm", "5-15cm", "15-30cm"],
        "value": "mean"
    }
    try:
        response = requests.get(url, params=params, timeout=7)
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
    live_climate = fetch_nasa_power_data(lat, lon)
    live_soil = fetch_soilgrids_data(lat, lon)

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
        # Intelligently pick nearest representative climate zone
        if abs(lat) < 23.5:
            ref = PRESETS["Nakuru, Rift Valley, Kenya (Equatorial Highland)"]
        elif abs(lat) > 45.0:
            ref = PRESETS["Poltava, Ukraine (Eurasian Chernozem Steppe)"]
        elif lon > 60:
            ref = PRESETS["Ludhiana, Punjab, India (Indo-Gangetic Plain)"]
        elif lat < 0:
            ref = PRESETS["Dubbo, New South Wales, Australia (Murray-Darling)"]
        elif lon < -98:
            ref = PRESETS["Lubbock, Texas, USA (Semi-Arid High Plains)"]
        else:
            ref = PRESETS["Ames, Iowa, USA (Humid Corn Belt)"]

        climate = live_climate if live_climate else {
            **ref["fallback_climate"],
            "source": "NASA POWER Regional Reference Baseline"
        }
        soil = live_soil if live_soil else {
            **ref["fallback_soil"],
            "source": "ISRIC SoilGrids Regional Baseline"
        }
    return climate, soil

# ---------------------------------------------------------
# CROP DATABASE (FAO GROUNDED)
# ---------------------------------------------------------
@st.cache_data
def load_crop_database():
    crops_path = os.path.join(os.path.dirname(__file__), "crops.csv")
    if os.path.exists(crops_path):
        return pd.read_csv(crops_path)
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
# DETERMINISTIC AGRONOMIC SCORING (STRICTLY PRESERVED)
# ---------------------------------------------------------
def generate_and_score_rotations(
    crop_df: pd.DataFrame,
    past_crops: list,
    weights: dict,
    climate_data: dict,
    soil_data: dict
):
    crops_list = crop_df.to_dict(orient="records")
    crop_by_name = {c["crop_name"]: c for c in crops_list}

    c_past1 = crop_by_name.get(past_crops[1], crops_list[0])

    candidates = []
    
    for c1 in crops_list:
        if c1["plant_family"] == c_past1["plant_family"] and "Cover" not in c1["crop_name"]:
            continue
        
        for c2 in crops_list:
            if c2["plant_family"] == c1["plant_family"] and "Cover" not in c2["crop_name"]:
                continue
            
            for c3 in crops_list:
                if c3["plant_family"] == c2["plant_family"] and "Cover" not in c3["crop_name"]:
                    continue
                
                seq = [c1, c2, c3]
                legume_count = sum(1 for c in seq if c["nitrogen_fixing"] == "Yes")
                if legume_count < 1:
                    continue
                
                if c1["crop_id"] == c2["crop_id"] == c3["crop_id"]:
                    continue
                
                total_water_need = sum(c["water_need_mm"] for c in seq)
                annual_water_need = total_water_need / 3.0
                mean_rainfall = climate_data["mean_annual_rainfall_mm"]
                water_ratio = annual_water_need / max(mean_rainfall, 250)
                
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
                
                if climate_data["mean_annual_rainfall_mm"] < 550:
                    drought_tol_count = sum(1 for c in seq if c["drought_tolerance"] == "High")
                    s_water = min(100.0, s_water + drought_tol_count * 5.0)

                n_fix_bonus = legume_count * 15.0
                residue_bonus = sum(12.0 for c in seq if c["soil_cover_residue"] == "High") + sum(6.0 for c in seq if c["soil_cover_residue"] == "Moderate")
                deep_root_bonus = sum(10.0 for c in seq if c["rooting_depth_m"] >= 1.5)
                family_count = len(set(c["plant_family"] for c in seq))
                diversity_bonus = family_count * 8.0
                s_soil = min(100.0, 20.0 + n_fix_bonus + residue_bonus + deep_root_bonus + diversity_bonus)

                risk_penalty = sum(15.0 for c in seq if c["economic_risk"] == "High") + sum(5.0 for c in seq if c["economic_risk"] == "Moderate")
                s_econ = max(30.0, 100.0 - risk_penalty)

                hot_days = climate_data["hot_days_per_year"]
                dry_spells = climate_data["dry_spells_per_year"]
                heat_fit = sum(12.0 for c in seq if c["heat_tolerance"] == "High") + sum(6.0 for c in seq if c["heat_tolerance"] == "Moderate")
                drought_fit = sum(12.0 for c in seq if c["drought_tolerance"] == "High") + sum(6.0 for c in seq if c["drought_tolerance"] == "Moderate")
                
                base_climate_stress = (hot_days * 0.4) + (dry_spells * 5.0)
                s_resilience = min(100.0, max(30.0, 50.0 + (heat_fit + drought_fit) - (base_climate_stress * 0.25)))

                soil_ph = soil_data.get("ph", 6.8)
                ph_mismatch = 0
                for c in seq:
                    if soil_ph < c["ph_min"] or soil_ph > c["ph_max"]:
                        ph_mismatch += 1
                ph_penalty = ph_mismatch * 8.0

                w_tot = sum(weights.values())
                composite_score = (
                    weights["water"] * s_water +
                    weights["soil"] * s_soil +
                    weights["econ"] * s_econ +
                    weights["resilience"] * s_resilience
                ) / max(w_tot, 1)
                composite_score = max(10.0, composite_score - ph_penalty)

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
    crop_by_name = {c["crop_name"]: c for c in crop_df.to_dict(orient="records")}
    crop = crop_by_name.get(past_crop_name, list(crop_by_name.values())[0])
    
    s_water = 60.0 if crop["water_need_mm"] <= climate_data["mean_annual_rainfall_mm"] else 35.0
    s_soil = 30.0 if crop["nitrogen_fixing"] == "No" else 55.0
    s_econ = 65.0
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
# UNIFIED VAULT PLOTLY TEMPLATE (DARK / TRON AESTHETICS)
# ---------------------------------------------------------
def apply_vault_plotly_theme(fig, title_text=""):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(10, 17, 24, 0.75)",
        title=dict(
            text=f"<span style='font-family: Orbitron; font-size: 11px; color: #19F3FF; letter-spacing: 1px;'>// {title_text.upper()}</span>",
            font=dict(family="Orbitron, monospace", color="#19F3FF"),
            x=0.01,
            y=0.98,
            xanchor="left",
            yanchor="top"
        ),
        font=dict(family="Rajdhani, sans-serif", color="#E8F6FF", size=13),
        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(25, 243, 255, 0.08)",
            linecolor="rgba(25, 243, 255, 0.25)",
            tickfont=dict(family="Share Tech Mono, monospace", color="#8FA6B8", size=11),
            zerolinecolor="rgba(25, 243, 255, 0.15)"
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(25, 243, 255, 0.08)",
            linecolor="rgba(25, 243, 255, 0.25)",
            tickfont=dict(family="Share Tech Mono, monospace", color="#8FA6B8", size=11),
            zerolinecolor="rgba(25, 243, 255, 0.15)"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1.0,
            bgcolor="rgba(10, 17, 24, 0.75)",
            bordercolor="rgba(25, 243, 255, 0.25)",
            borderwidth=1,
            font=dict(family="Rajdhani, sans-serif", color="#E8F6FF", size=10)
        ),
        hoverlabel=dict(
            bgcolor="#0A1118",
            bordercolor="#19F3FF",
            font=dict(family="Share Tech Mono, monospace", color="#FFFFFF", size=12)
        ),
        margin=dict(l=30, r=30, t=55, b=30)
    )
    return fig

# ---------------------------------------------------------
# ARC-REACTOR STYLE CIRCULAR GAUGE RENDERER
# ---------------------------------------------------------
def render_arc_gauge(score: float, label: str, color: str = "#19F3FF"):
    pct = max(0, min(100, int(score)))
    deg = int(pct * 3.6)
    return f"""<div class="arc-gauge-container"><div class="arc-gauge" style="background: conic-gradient({color} 0deg {deg}deg, rgba(25, 243, 255, 0.08) {deg}deg 360deg);"><div class="arc-gauge-inner"><div class="arc-score" style="color: {color};">{pct}</div></div></div><div class="arc-label">{label}</div></div>"""

# ---------------------------------------------------------
# APPLICATION STATE & BIDIRECTIONAL GLOBE HOOK
# ---------------------------------------------------------
crop_df = load_crop_database()

# Declare Custom Bidirectional Component
globe_component_dir = os.path.join(os.path.dirname(__file__), "globe_component")
globe_component = components.declare_component("globe_component", path=globe_component_dir)

# Initialize Session State Variables
if "location_mode_radio" not in st.session_state:
    st.session_state["location_mode_radio"] = "Benchmark Farm"
if "custom_lat_input" not in st.session_state:
    st.session_state["custom_lat_input"] = 33.5779
if "custom_lon_input" not in st.session_state:
    st.session_state["custom_lon_input"] = -101.8552
if "last_locked_id" not in st.session_state:
    st.session_state["last_locked_id"] = None
if "prev_lat" not in st.session_state:
    st.session_state.prev_lat = 33.5779
    st.session_state.prev_lon = -101.8552
    st.session_state.is_first_load = True
else:
    st.session_state.is_first_load = False

# Check if a target lock was received from the 3D globe component
globe_val = st.session_state.get("globe_selector")
if isinstance(globe_val, dict) and globe_val.get("id"):
    if globe_val.get("id") != st.session_state.get("last_locked_id"):
        st.session_state["last_locked_id"] = globe_val["id"]
        st.session_state["location_mode_radio"] = "Custom Coordinates"
        st.session_state["custom_lat_input"] = float(globe_val["lat"])
        st.session_state["custom_lon_input"] = float(globe_val["lon"])
        st.toast(f"🎯 Target Locked: {globe_val['lat']:+.4f}°, {globe_val['lon']:+.4f}°", icon="🛰️")

# SIDEBAR: THE COMMAND PANEL
render_html("""<div style="font-family: 'Orbitron', monospace; font-size: 1.15rem; font-weight: 800; color: #19F3FF; letter-spacing: 2px; margin-bottom: 12px; text-transform: uppercase;">⚡ COMMAND PANEL</div>""", sidebar=True)

st.sidebar.markdown("### // 01 SECTOR SELECT")
location_mode = st.sidebar.radio(
    "Coordinate Source:",
    ["Benchmark Farm", "Custom Coordinates"],
    key="location_mode_radio"
)

if location_mode == "Benchmark Farm":
    selected_preset = st.sidebar.selectbox("Benchmark Sector:", list(PRESETS.keys()), index=0, key="preset_select")
    farm_info = PRESETS[selected_preset]
    latitude = float(farm_info["lat"])
    longitude = float(farm_info["lon"])
    location_display_name = selected_preset
else:
    selected_preset = None
    latitude = float(st.sidebar.number_input(
        "Latitude (°N/S):",
        min_value=-60.0,
        max_value=75.0,
        step=0.01,
        key="custom_lat_input"
    ))
    longitude = float(st.sidebar.number_input(
        "Longitude (°E/W):",
        min_value=-180.0,
        max_value=180.0,
        step=0.01,
        key="custom_lon_input"
    ))
    location_display_name = f"Custom Field ({latitude:+.4f}°, {longitude:+.4f}°)"

st.sidebar.markdown("### // 02 CROPPING LOG")
available_crops = crop_df["crop_name"].tolist()
default_past1 = farm_info["default_past_crops"][0] if selected_preset else available_crops[0]
default_past2 = farm_info["default_past_crops"][1] if selected_preset else available_crops[1]

past_crop_2 = st.sidebar.selectbox("Season -2 Crop:", available_crops, index=available_crops.index(default_past1) if default_past1 in available_crops else 0, key="past_c2")
past_crop_1 = st.sidebar.selectbox("Season -1 Crop:", available_crops, index=available_crops.index(default_past2) if default_past2 in available_crops else 1, key="past_c1")

st.sidebar.markdown("### // 03 TACTICAL PRIORITIES")
w_water = st.sidebar.slider("💧 Water Conservation", 1, 5, 4, key="sl_water")
w_soil = st.sidebar.slider("🪵 Soil Health & Organic Carbon", 1, 5, 5, key="sl_soil")
w_econ = st.sidebar.slider("📈 Market / Income Stability", 1, 5, 3, key="sl_econ")
w_resilience = st.sidebar.slider("☀️ Thermal & Drought Resilience", 1, 5, 4, key="sl_resil")

st.sidebar.markdown("### // 04 SOIL TEST OVERRIDE")
use_custom_soil = st.sidebar.checkbox("Manual Soil Lab Override", value=False, key="chk_override")

override_clay = st.sidebar.number_input("Clay Content (%)", 0.0, 100.0, 24.0, key="num_clay") if use_custom_soil else 24.0
override_sand = st.sidebar.number_input("Sand Content (%)", 0.0, 100.0, 52.0, key="num_sand") if use_custom_soil else 52.0
override_soc = st.sidebar.number_input("Organic Carbon (%)", 0.0, 20.0, 1.2, key="num_soc") if use_custom_soil else 1.2
override_ph = st.sidebar.number_input("Soil pH", 3.5, 9.5, 7.2, key="num_ph") if use_custom_soil else 7.2

# Fetch NASA Climate & ISRIC Soil Data
climate_data, base_soil_data = get_climate_and_soil(latitude, longitude, selected_preset)

# Validate Farmland vs Ocean/Ice
is_farmland = check_is_farmland(latitude, longitude, base_soil_data)

btn_analyze = st.sidebar.button(
    "⚡ INITIALIZE TACTICAL ANALYSIS",
    use_container_width=True,
    disabled=not is_farmland
)

user_weights = {
    "water": float(w_water),
    "soil": float(w_soil),
    "econ": float(w_econ),
    "resilience": float(w_resilience)
}

if use_custom_soil:
    active_soil_data = {
        "clay_pct": override_clay,
        "sand_pct": override_sand,
        "soc_pct": override_soc,
        "ph": override_ph,
        "source": "Farmer Lab Test (Manual Override)"
    }
else:
    active_soil_data = base_soil_data

# Real Status Indicators
is_nasa_live = "Live" in climate_data.get("source", "")
nasa_chip_class = "chip-active" if is_nasa_live else "chip-fallback"
nasa_chip_text = "🟢 NASA POWER LINK: ACTIVE" if is_nasa_live else "🟡 NASA ARCHIVE / FALLBACK ACTIVE"

# ---------------------------------------------------------
# TOP COMMAND BAR
# ---------------------------------------------------------
command_bar_html = f"""<div class="command-bar"><div><div class="command-title">FIELDSHIFT ROTATION ADVISOR</div><div class="command-subtitle">EARTH OBSERVATION DECISION INTELLIGENCE • NASA SPACE APPS 2026</div></div><div class="status-chip-container"><div class="status-chip {nasa_chip_class}">{nasa_chip_text}</div><div class="status-chip chip-target">📍 TARGET: {latitude:+.2f}°, {longitude:+.2f}°</div></div></div>"""
render_html(command_bar_html)

# ---------------------------------------------------------
# HERO 3D COCKPIT VIEWPORT (BIDIRECTIONAL GLOBE)
# ---------------------------------------------------------
# Invoke the two-way Globe component
globe_component(
    target_lat=latitude,
    target_lon=longitude,
    target_label=location_display_name,
    is_first_load=st.session_state.is_first_load,
    key="globe_selector"
)

# Update session continuity
st.session_state.prev_lat = latitude
st.session_state.prev_lon = longitude

# ---------------------------------------------------------
# NON-FARMLAND / OCEAN SAFEGUARD BANNER
# ---------------------------------------------------------
if not is_farmland:
    ocean_warning_html = f"""<div style="background: rgba(255, 59, 59, 0.15); border: 1px solid #FF3B3B; border-radius: 8px; padding: 16px 20px; margin: 18px 0; font-family: 'Share Tech Mono', monospace; color: #FF3B3B; box-shadow: 0 0 24px rgba(255,59,59,0.25);"><div style="font-family: 'Orbitron', monospace; font-size: 1.05rem; font-weight: 800; letter-spacing: 1.5px; display: flex; align-items: center; gap: 8px;"><span>⚠️ SENSOR WARNING</span> // NO FARMLAND DATA AT THIS POINT</div><div style="font-size: 0.9rem; margin-top: 6px; color: #E8F6FF; line-height: 1.5;">The crosshair reticle is currently positioned over open water, polar ice, or non-arable maritime coordinates ({latitude:+.4f}°, {longitude:+.4f}°). Rotate the 3D globe to a continental agricultural region, align the reticle, and click <strong>LOCK TARGET</strong> to calibrate analysis.</div></div>"""
    render_html(ocean_warning_html)

# ---------------------------------------------------------
# MODULE 01: CLIMATE INTEL & SOIL PROFILE
# ---------------------------------------------------------
render_html(f'<div class="module-header">01 // CLIMATE & SOIL INTEL (NASA POWER 15-YR RECORD) — {location_display_name.upper()}</div>')

col_m1, col_m2, col_m3, col_m4 = st.columns(4)
with col_m1:
    m1_html = f"""<div class="holo-metric-card"><div class="holo-label">ANNUAL PRECIPITATION</div><div class="holo-val">{climate_data['mean_annual_rainfall_mm']} <span style="font-size:0.9rem; color:#8FA6B8;">mm</span></div><div class="holo-delta {'positive' if climate_data['rainfall_trend_pct'] >= 0 else 'amber'}">DECADE TREND: {climate_data['rainfall_trend_pct']:+.1f}%</div></div>"""
    render_html(m1_html)

with col_m2:
    m2_html = f"""<div class="holo-metric-card"><div class="holo-label">MEAN TEMPERATURE</div><div class="holo-val">{climate_data['mean_annual_temp_c']} <span style="font-size:0.9rem; color:#8FA6B8;">°C</span></div><div class="holo-delta amber">WARMING: +{climate_data['warming_rate_c_decade']:.2f} °C / DECADE</div></div>"""
    render_html(m2_html)

with col_m3:
    m3_html = f"""<div class="holo-metric-card"><div class="holo-label">EXTREME HEAT EXPOSURE</div><div class="holo-val">{climate_data['hot_days_per_year']} <span style="font-size:0.9rem; color:#8FA6B8;">DAYS/YR</span></div><div class="holo-delta amber">THRESHOLD: >35°C PEAK TEMP</div></div>"""
    render_html(m3_html)

with col_m4:
    soc_display = f"{active_soil_data['soc_pct']:.2f}" if is_farmland else "N/A"
    texture_display = f"{active_soil_data['clay_pct']}% CLAY | pH {active_soil_data['ph']}" if is_farmland else "OPEN WATER"
    m4_html = f"""<div class="holo-metric-card"><div class="holo-label">SOIL ORGANIC CARBON (SOC)</div><div class="holo-val">{soc_display} <span style="font-size:0.9rem; color:#8FA6B8;">%</span></div><div class="holo-delta {'positive' if is_farmland else 'amber'}">TEXTURE: {texture_display}</div></div>"""
    render_html(m4_html)

# ---------------------------------------------------------
# MODULE 02: ROTATION STRATEGY BENCHMARKING
# ---------------------------------------------------------
render_html(f'<div class="module-header">02 // TACTICAL ROTATION STRATEGIES (RANKED VS. STATUS QUO) — {location_display_name.upper()}</div>')

if not is_farmland:
    st.info("Cropping rotation optimization paused: Target coordinates are over non-arable terrain. Select a terrestrial farm location to generate crop sequence models.")
else:
    top_rotations = generate_and_score_rotations(
        crop_df,
        [past_crop_2, past_crop_1],
        user_weights,
        climate_data,
        active_soil_data
    )
    baseline = evaluate_baseline_monoculture(past_crop_1, crop_df, climate_data, active_soil_data, user_weights)

    if not top_rotations:
        st.warning("No rotation sequence satisfied current constraints. Adjust field cropping parameters.")
    else:
        for idx, r in enumerate(top_rotations[:3]):
            is_top = (idx == 0)
            card_class = "rotation-hero-card rank-1" if is_top else "rotation-hero-card"
            badge_class = "rank-badge gold" if is_top else "rank-badge cyan"
            badge_text = f"★ RANK #{idx+1} OPTIMAL STRATEGY (COMPOSITE {r['composite_score']}/100)" if is_top else f"RANK #{idx+1} ALTERNATIVE ({r['composite_score']}/100)"
            
            crops = r["crops"]
            timeline_html = f"""<div class="crop-timeline"><div class="crop-node">SEASON 1: {crops[0]}</div><div class="crop-arrow">➔</div><div class="crop-node">SEASON 2: {crops[1]}</div><div class="crop-arrow">➔</div><div class="crop-node">SEASON 3: {crops[2]}</div></div>"""
            
            gauges_html = f"""<div class="gauge-grid">{render_arc_gauge(r['s_water'], 'WATER FIT', '#19F3FF')}{render_arc_gauge(r['s_soil'], 'SOIL HEALTH', '#2CFFB0')}{render_arc_gauge(r['s_resilience'], 'RESILIENCE', '#FF9E1F')}{render_arc_gauge(r['s_econ'], 'MARKET STABILITY', '#80F9FF')}</div>"""
            
            water_saved = baseline["annual_water_need_mm"] - r["annual_water_need_mm"]
            diff_text = f"Conserves {water_saved} mm water/yr vs. continuous {baseline['crop_name']}" if water_saved > 0 else f"Water demand +{-water_saved} mm/yr"
            
            card_html = f"""<div class="{card_class}"><div class="{badge_class}">{badge_text}</div>{timeline_html}{gauges_html}<div style="font-family: 'Share Tech Mono', monospace; font-size: 0.85rem; color: #8FA6B8; margin-top: 8px;"><span style="color: #2CFFB0;">HYDROL-IMPACT:</span> {diff_text} • <span style="color: #19F3FF;">BIODIVERSITY:</span> {r['legume_seasons']} Legume Season(s) • {len(r['families'])} Families</div><div style="margin-top: 10px; font-family: 'Rajdhani', sans-serif; font-size: 0.95rem; color: #E8F6FF; line-height: 1.5; border-left: 2px solid #19F3FF; padding-left: 12px;"><strong>AGRONOMIC RATIONALE:</strong> {r['rationale']}</div></div>"""
            render_html(card_html)

# ---------------------------------------------------------
# MODULE 03: INTERACTIVE CHARTS & DIAGNOSTICS
# ---------------------------------------------------------
render_html(f'<div class="module-header">03 // ADVANCED DIAGNOSTICS & COMPARATIVE GRAPHS — {location_display_name.upper()}</div>')

tab1, tab2, tab3, tab4 = st.tabs([
    "📈 15-YR CLIMATE INTEL",
    "💧 WATER BUDGET MATRIX",
    "🗺️ SENSOR MAP & SOIL",
    "📚 FAO SOURCES & DATA"
])

with tab1:
    df_climate_series = pd.DataFrame(climate_data["annual_series"])
    col_c1, col_c2 = st.columns(2)
    
    with col_c1:
        fig_rain = go.Figure()
        fig_rain.add_trace(go.Bar(
            x=df_climate_series["year"],
            y=df_climate_series["rain"],
            name="Precipitation (mm)",
            marker=dict(color="#19F3FF", opacity=0.85)
        ))
        fig_rain.add_hline(
            y=climate_data["mean_annual_rainfall_mm"],
            line_dash="dash",
            line_color="#2CFFB0",
            annotation_text=f"15-yr Normal: {climate_data['mean_annual_rainfall_mm']} mm",
            annotation_font=dict(color="#2CFFB0", family="Share Tech Mono")
        )
        apply_vault_plotly_theme(fig_rain, f"ANNUAL RAINFALL VS. 15-YR NORMAL — {location_display_name}")
        st.plotly_chart(fig_rain, use_container_width=True)

    with col_c2:
        fig_temp = go.Figure()
        fig_temp.add_trace(go.Scatter(
            x=df_climate_series["year"],
            y=df_climate_series["temp"],
            name="Mean Temp (°C)",
            mode="lines+markers",
            line=dict(color="#FFFFFF", width=2.5),
            marker=dict(color="#19F3FF", size=6)
        ))
        fig_temp.add_trace(go.Bar(
            x=df_climate_series["year"],
            y=df_climate_series["hot_days"],
            name="Hot Days (>35°C)",
            marker=dict(color="#FF9E1F", opacity=0.65),
            yaxis="y2"
        ))
        fig_temp.update_layout(
            yaxis2=dict(
                title=dict(text="Hot Days Count", font=dict(color="#FF9E1F")),
                overlaying="y",
                side="right",
                showgrid=False,
                tickfont=dict(family="Share Tech Mono", color="#FF9E1F")
            )
        )
        apply_vault_plotly_theme(fig_temp, f"TEMPERATURE & EXTREME HEAT TREND — {location_display_name}")
        st.plotly_chart(fig_temp, use_container_width=True)

with tab2:
    if is_farmland and 'top_rotations' in locals() and top_rotations:
        comp_labels = ["Current Practice"] + [f"Rank #{i+1}" for i in range(min(3, len(top_rotations)))]
        water_values = [baseline["annual_water_need_mm"]] + [r["annual_water_need_mm"] for r in top_rotations[:3]]

        col_w1, col_w2 = st.columns(2)
        with col_w1:
            fig_water = go.Figure()
            fig_water.add_trace(go.Bar(
                x=comp_labels,
                y=water_values,
                name="Annual Water Need (mm)",
                marker=dict(color=["#FF3B3B", "#2CFFB0", "#19F3FF", "#80F9FF"], opacity=0.85)
            ))
            fig_water.add_hline(
                y=climate_data["mean_annual_rainfall_mm"],
                line_dash="dot",
                line_color="#19F3FF",
                line_width=2,
                annotation_text=f"NASA Rain: {climate_data['mean_annual_rainfall_mm']} mm",
                annotation_font=dict(color="#19F3FF", family="Share Tech Mono")
            )
            apply_vault_plotly_theme(fig_water, f"WATER DEMAND VS. NASA RAIN ENVELOPE — {location_display_name}")
            st.plotly_chart(fig_water, use_container_width=True)

        with col_w2:
            categories = ["Water Fit", "Soil Health", "Climate Resilience", "Market Stability"]
            fig_radar = go.Figure()
            
            fig_radar.add_trace(go.Scatterpolar(
                r=[baseline["s_water"], baseline["s_soil"], baseline["s_resilience"], baseline["s_econ"]],
                theta=categories,
                fill="toself",
                name="Current Practice",
                line=dict(color="#FF3B3B", width=2),
                fillcolor="rgba(255, 59, 59, 0.15)"
            ))
            
            r1 = top_rotations[0]
            fig_radar.add_trace(go.Scatterpolar(
                r=[r1["s_water"], r1["s_soil"], r1["s_resilience"], r1["s_econ"]],
                theta=categories,
                fill="toself",
                name="Rank #1 Strategy",
                line=dict(color="#19F3FF", width=2.5),
                fillcolor="rgba(25, 243, 255, 0.22)"
            ))

            fig_radar.update_layout(
                polar=dict(
                    bgcolor="rgba(10, 17, 24, 0.8)",
                    radialaxis=dict(visible=True, range=[0, 100], gridcolor="rgba(25, 243, 255, 0.15)", tickfont=dict(family="Share Tech Mono", color="#8FA6B8")),
                    angularaxis=dict(gridcolor="rgba(25, 243, 255, 0.15)", tickfont=dict(family="Rajdhani", color="#E8F6FF", size=12))
                ),
                showlegend=True
            )
            apply_vault_plotly_theme(fig_radar, f"AGRONOMIC RESILIENCE MATRIX — {location_display_name}")
            st.plotly_chart(fig_radar, use_container_width=True)
    else:
        st.info("Water budget matrix and agronomic radar require arable terrestrial coordinates.")

with tab3:
    col_map1, col_map2 = st.columns([0.65, 0.35])
    
    with col_map1:
        fig_map = go.Figure(go.Scattermapbox(
            lat=[latitude],
            lon=[longitude],
            mode='markers+text',
            marker=dict(size=18, color='#FF9E1F' if not is_farmland else '#19F3FF', opacity=0.9),
            text=[location_display_name],
            textposition="top right",
            textfont=dict(family="Share Tech Mono", size=12, color="#19F3FF")
        ))
        fig_map.update_layout(
            mapbox=dict(
                style="carto-darkmatter",
                center=dict(lat=latitude, lon=longitude),
                zoom=4.0
            ),
            margin=dict(l=0, r=0, t=0, b=0),
            height=360
        )
        st.plotly_chart(fig_map, use_container_width=True)

    with col_map2:
        soil_profile_html = f"""<div class="holo-metric-card" style="height: 360px;"><div class="holo-label">SOIL PROFILE (ISRIC SOILGRIDS 0–30 CM)</div><div style="margin-top: 10px; font-family: 'Share Tech Mono', monospace; font-size: 0.95rem; line-height: 1.8;"><div>CLAY FRACTION: <span style="color:#19F3FF;">{active_soil_data['clay_pct']}%</span></div><div>SAND FRACTION: <span style="color:#19F3FF;">{active_soil_data['sand_pct']}%</span></div><div>ORGANIC CARBON: <span style="color:#2CFFB0;">{active_soil_data['soc_pct']}%</span></div><div>SOIL pH (H2O): <span style="color:#FF9E1F;">{active_soil_data['ph']}</span></div></div><div style="margin-top: 14px; font-size: 0.85rem; color: #8FA6B8; line-height: 1.4;"><em>AGRONOMIC INTEL:</em> Soil texture regulates water-holding capacity and root aeration. Diverse crop root profiles buffer seasonal precipitation volatility.</div></div>"""
        render_html(soil_profile_html)

with tab4:
    render_html('<div class="module-header">04 // SCIENTIFIC METHODOLOGY & REFERENCES</div>')
    st.dataframe(crop_df, use_container_width=True, hide_index=True)
    sources_html = """<div style="font-family: 'Rajdhani', sans-serif; font-size: 0.95rem; color: #8FA6B8; line-height: 1.6; margin-top: 12px;"><p><strong style="color: #19F3FF;">1. NASA POWER Project (Prediction Of Worldwide Energy Resources):</strong> Daily agroclimatology dataset (T2M, T2M_MAX, PRECTOTCORR). NASA Langley Research Center. API: <code>https://power.larc.nasa.gov/api/temporal/daily/point</code>.</p><p><strong style="color: #19F3FF;">2. ISRIC SoilGrids 250m v2.0:</strong> Global gridded soil information system. API: <code>https://rest.isric.org/soilgrids/v2.0/properties/query</code>.</p><p><strong style="color: #19F3FF;">3. FAO Irrigation & Drainage Papers No. 56 & 33:</strong> Guidelines for crop water requirements and yield response to water deficits. Food and Agriculture Organization of the United Nations.</p><p><strong style="color: #19F3FF;">4. Planetary Textures:</strong> NASA Blue Marble and Earth at Night imagery compiled by the NASA Earth Observatory, served via three-globe.</p></div>"""
    render_html(sources_html)

# Footer
st.markdown("---")
footer_html = """<div style="text-align: center; font-family: 'Share Tech Mono', monospace; font-size: 0.8rem; color: #546B7E; letter-spacing: 1px;">FIELDSHIFT TACTICAL ROTATION ADVISOR • NASA SPACE APPS CHALLENGE 2026 • OPEN SCIENCE DECISION SUPPORT</div>"""
render_html(footer_html)
