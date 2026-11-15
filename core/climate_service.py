"""
FieldShift NASA POWER Agroclimatology Service.
Fetches daily point meteorological parameters (T2M, T2M_MAX, PRECTOTCORR) from NASA Langley Research Center
and computes long-term agroclimatic indicators.
"""

import math
import requests
import numpy as np
import pandas as pd
import streamlit as st

@st.cache_data(show_spinner=False, ttl=86400)
def fetch_nasa_power_data(lat: float, lon: float):
    """
    Fetches 15-year daily meteorological time series (2010-2024) from the NASA POWER API.
    Computes rainfall totals, extreme heat days (>35C), warming trends, and dry-spell frequency.
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
                "source": "NASA POWER API (Live Satellite / Reanalysis)",
                "mean_annual_rainfall_mm": round(mean_rain, 1),
                "rainfall_trend_pct": round((rain_slope * 10 / max(mean_rain, 1)) * 100, 1),
                "mean_annual_temp_c": round(mean_temp, 1),
                "warming_rate_c_decade": round(temp_slope * 10, 2),
                "hot_days_per_year": avg_hot,
                "dry_spells_per_year": round(avg_dry, 1),
                "annual_series": annual_series,
                "provenance": "LIVE API"
            }
    except Exception:
        pass
    return None

def calculate_climate_indicators(annual_series: list, source_label: str = "DERIVED") -> dict:
    """
    Computes climate averages and decadal trend slopes from an annual series.
    """
    df_s = pd.DataFrame(annual_series)
    mean_rain = float(df_s["rain"].mean())
    mean_temp = float(df_s["temp"].mean())
    avg_hot = int(df_s["hot_days"].mean())
    avg_dry = float(df_s.get("dry_spells", pd.Series([2])).mean())
    
    years_arr = df_s["year"].values
    rain_slope = float(np.polyfit(years_arr, df_s["rain"].values, 1)[0])
    temp_slope = float(np.polyfit(years_arr, df_s["temp"].values, 1)[0])

    return {
        "source": source_label,
        "mean_annual_rainfall_mm": round(mean_rain, 1),
        "rainfall_trend_pct": round((rain_slope * 10 / max(mean_rain, 1)) * 100, 1),
        "mean_annual_temp_c": round(mean_temp, 1),
        "warming_rate_c_decade": round(temp_slope * 10, 2),
        "hot_days_per_year": avg_hot,
        "dry_spells_per_year": round(avg_dry, 1),
        "annual_series": annual_series
    }
