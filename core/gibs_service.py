"""
FieldShift NASA GIBS Satellite Imagery Service.
Resolves multi-layer satellite telemetry from NASA GIBS WMTS REST API (EPSG:3857).
Supports True Color, MODIS NDVI, GPM IMERG Precipitation, SMAP Soil Moisture,
and Blue Marble Basemap with full provenance disclosures.
"""

import math
import urllib.request
from datetime import datetime, timedelta, timezone

GIBS_LAYERS = {
    "true_color": {
        "title": "NASA GIBS MODIS Terra (True Color)",
        "layer_id": "MODIS_Terra_CorrectedReflectance_TrueColor",
        "matrix_set": "GoogleMapsCompatible_Level9",
        "format": "jpg",
        "max_zoom": 9,
        "is_daily": True,
        "resolution": "250m at nadir (daily optical)",
        "provenance": "LIVE API (NASA EOSDIS GIBS)",
        "disclaimer": "Visible spectrum reflectance showing broad surface features, vegetation greenness, and cloud cover. Not a field-scale drone orthomosaic."
    },
    "ndvi": {
        "title": "NASA GIBS MODIS 16-Day NDVI (Vegetation Index)",
        "layer_id": "MODIS_Terra_NDVI_16Day",
        "matrix_set": "GoogleMapsCompatible_Level9",
        "format": "png",
        "max_zoom": 9,
        "is_daily": False,
        "resolution": "250m composite (16-day cycle)",
        "provenance": "DERIVED (NASA EOSDIS GIBS)",
        "disclaimer": "Normalized Difference Vegetation Index tracking relative photosynthetic vigor and canopy greenness across regional landscapes."
    },
    "precipitation": {
        "title": "NASA GPM IMERG Daily Precipitation Rate",
        "layer_id": "IMERG_Precipitation_Rate",
        "matrix_set": "GoogleMapsCompatible_Level6",
        "format": "png",
        "max_zoom": 6,
        "is_daily": True,
        "resolution": "~10km (0.1° grid)",
        "provenance": "LIVE API (NASA GPM IMERG)",
        "disclaimer": "Satellite microwave-infrared merged precipitation flux. Coarse resolution indicates regional storm systems, not farm-scale rain gauges."
    },
    "soil_moisture": {
        "title": "NASA SMAP L3 Surface Soil Moisture (0-5cm)",
        "layer_id": "SMAP_L3_Passive_Enhanced_Soil_Moisture_Surface",
        "matrix_set": "GoogleMapsCompatible_Level6",
        "format": "png",
        "max_zoom": 6,
        "is_daily": True,
        "resolution": "9km enhanced grid",
        "provenance": "MODELED / SIMULATED (NASA SMAP)",
        "disclaimer": "Top 5cm surface dielectric volumetric water content. Useful for regional drought monitoring; does not capture subsoil rooting zone moisture."
    },
    "blue_marble": {
        "title": "NASA GIBS Blue Marble (Topography & Bathymetry)",
        "layer_id": "BlueMarble_ShadedRelief_Bathymetry",
        "matrix_set": "GoogleMapsCompatible_Level8",
        "format": "jpg",
        "max_zoom": 8,
        "is_daily": False,
        "resolution": "500m global baseline",
        "provenance": "APPROXIMATE TABLE (NASA GIBS)",
        "disclaimer": "Static global composite terrain baseline."
    }
}

def get_layer_tile_url(layer_key: str, imagery_date: str = None) -> tuple:
    """
    Constructs the NASA GIBS REST tile URL pattern for a selected satellite layer.
    """
    layer_info = GIBS_LAYERS.get(layer_key, GIBS_LAYERS["true_color"])
    layer_id = layer_info["layer_id"]
    tms = layer_info["matrix_set"]
    ext = layer_info["format"]
    
    if layer_info["is_daily"]:
        if not imagery_date:
            now_utc = datetime.now(timezone.utc)
            imagery_date = (now_utc - timedelta(days=2)).strftime("%Y-%m-%d")
        url = f"https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/{layer_id}/default/{imagery_date}/{tms}/{{z}}/{{y}}/{{x}}.{ext}"
    else:
        url = f"https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/{layer_id}/default/default/{tms}/{{z}}/{{y}}/{{x}}.{ext}"
        imagery_date = "Static Baseline"

    return url, layer_info["title"], imagery_date, layer_info["max_zoom"], layer_info["resolution"], layer_info["disclaimer"]

def get_verified_gibs_tile_url(lat: float, lon: float):
    """
    Backward-compatible resolver for Mission Control basemap.
    """
    url, title, date_str, max_z, _, _ = get_layer_tile_url("true_color")
    try:
        lat_rad = math.radians(lat)
        n = 16.0
        xtile = int((lon + 180.0) / 360.0 * n)
        ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
        test_url = url.replace("{z}", "4").replace("{y}", str(ytile)).replace("{x}", str(xtile))
        req = urllib.request.Request(test_url, headers={"User-Agent": "FieldShift/1.0"})
        with urllib.request.urlopen(req, timeout=2.0) as resp:
            if resp.status == 200:
                return url, title, date_str, max_z
    except Exception:
        pass
        
    return get_layer_tile_url("blue_marble")[:4]
