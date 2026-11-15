"""
FieldShift ISRIC SoilGrids 250m Service.
Fetches physical and chemical soil properties across the 0-30 cm root-zone profile:
- Clay fraction (%)
- Sand fraction (%)
- Soil Organic Carbon (SOC %)
- Soil pH (H2O)
"""

import requests
import numpy as np
import streamlit as st

@st.cache_data(show_spinner=False, ttl=86400)
def fetch_soilgrids_data(lat: float, lon: float):
    """
    Fetches gridded soil properties from the ISRIC SoilGrids 250m v2.0 REST API.
    Averages layers across 0-5cm, 5-15cm, and 15-30cm depths.
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
                "ph": ph,
                "provenance": "LIVE API"
            }
    except Exception:
        pass
    return None
