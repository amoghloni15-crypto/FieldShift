"""
FieldShift NASA GIBS Satellite Imagery Service.
Resolves true-color corrected reflectance satellite imagery from NASA GIBS WMTS REST API (EPSG:3857).
Provides automatic fallback to NASA Blue Marble Shaded Relief.
"""

import math
import urllib.request
from datetime import datetime, timedelta, timezone

def get_verified_gibs_tile_url(lat: float, lon: float):
    """
    Returns the active NASA GIBS WMTS satellite tile URL template, layer label, date, and max zoom.
    Primary layer: MODIS Terra Corrected Reflectance (True Color, GoogleMapsCompatible_Level9).
    Fallback layer: Blue Marble Shaded Relief & Bathymetry (Static, GoogleMapsCompatible_Level8).
    URL pattern: https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/{layer}/default/{date}/{tms}/{z}/{y}/{x}.jpg
    (Notice in GIBS REST WMTS, {TileRow} precedes {TileCol}, mapped to {y} and {x}).
    """
    now_utc = datetime.now(timezone.utc)
    imagery_date = (now_utc - timedelta(days=2)).strftime("%Y-%m-%d")
    primary_url = f"https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_CorrectedReflectance_TrueColor/default/{imagery_date}/GoogleMapsCompatible_Level9/{{z}}/{{y}}/{{x}}.jpg"
    fallback_url = "https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/BlueMarble_ShadedRelief_Bathymetry/default/default/GoogleMapsCompatible_Level8/{z}/{y}/{x}.jpg"
    
    try:
        lat_rad = math.radians(lat)
        n = 16.0  # 2^4 for zoom 4 check
        xtile = int((lon + 180.0) / 360.0 * n)
        ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
        test_url = primary_url.replace("{z}", "4").replace("{y}", str(ytile)).replace("{x}", str(xtile))
        req = urllib.request.Request(test_url, headers={"User-Agent": "FieldShift/1.0"})
        with urllib.request.urlopen(req, timeout=2.0) as resp:
            if resp.status == 200:
                return primary_url, "NASA GIBS MODIS Terra (True Color)", imagery_date, 9
    except Exception:
        pass
        
    return fallback_url, "NASA GIBS Blue Marble (Shaded Relief)", "Static", 8
