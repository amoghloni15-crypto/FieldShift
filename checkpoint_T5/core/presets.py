"""
FieldShift Global Benchmark Farms & Coordinate Validation.
Ground truth historical baselines for representative agro-ecological zones,
including international benchmarks and Indian regional agrarian corridors.
"""

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
    "Hubballi-Dharwad, Karnataka, India (Northern Transition Zone)": {
        "lat": 15.3647,
        "lon": 75.1240,
        "climate_type": "Semi-arid tropical transition (Black cotton vertisols, bimodal Kharif/Rabi seasons)",
        "default_past_crops": ["Grain Sorghum", "Chickpea (Garbanzo)"],
        "fallback_soil": {"clay_pct": 46.0, "sand_pct": 28.0, "soc_pct": 0.65, "ph": 7.8},
        "fallback_climate": {
            "mean_annual_rainfall_mm": 740.0,
            "rainfall_trend_pct": -3.5,
            "mean_annual_temp_c": 25.4,
            "warming_rate_c_decade": 0.28,
            "hot_days_per_year": 58,
            "dry_spells_per_year": 3.2,
            "annual_series": [
                {"year": 2010, "rain": 820, "temp": 25.1, "hot_days": 52},
                {"year": 2011, "rain": 710, "temp": 25.3, "hot_days": 56},
                {"year": 2012, "rain": 580, "temp": 25.8, "hot_days": 64},
                {"year": 2013, "rain": 760, "temp": 25.2, "hot_days": 54},
                {"year": 2014, "rain": 790, "temp": 25.4, "hot_days": 57},
                {"year": 2015, "rain": 620, "temp": 25.9, "hot_days": 68},
                {"year": 2016, "rain": 640, "temp": 26.0, "hot_days": 70},
                {"year": 2017, "rain": 780, "temp": 25.3, "hot_days": 55},
                {"year": 2018, "rain": 730, "temp": 25.5, "hot_days": 59},
                {"year": 2019, "rain": 910, "temp": 25.0, "hot_days": 48},
                {"year": 2020, "rain": 850, "temp": 25.2, "hot_days": 53},
                {"year": 2021, "rain": 790, "temp": 25.4, "hot_days": 56},
                {"year": 2022, "rain": 840, "temp": 25.3, "hot_days": 54},
                {"year": 2023, "rain": 610, "temp": 26.2, "hot_days": 72},
                {"year": 2024, "rain": 750, "temp": 25.7, "hot_days": 60},
            ]
        }
    },
    "Raichur, Karnataka, India (North Eastern Dry Zone)": {
        "lat": 16.2076,
        "lon": 77.3463,
        "climate_type": "Arid/Semi-arid Deccan plateau (High summer heat, erratic monsoon, deep cracking vertisols)",
        "default_past_crops": ["Pigeon Pea (Tur / Arhar)", "Grain Sorghum"],
        "fallback_soil": {"clay_pct": 38.0, "sand_pct": 35.0, "soc_pct": 0.52, "ph": 8.0},
        "fallback_climate": {
            "mean_annual_rainfall_mm": 620.0,
            "rainfall_trend_pct": -4.8,
            "mean_annual_temp_c": 27.8,
            "warming_rate_c_decade": 0.35,
            "hot_days_per_year": 112,
            "dry_spells_per_year": 4.6,
            "annual_series": [
                {"year": 2010, "rain": 690, "temp": 27.4, "hot_days": 105},
                {"year": 2011, "rain": 610, "temp": 27.6, "hot_days": 110},
                {"year": 2012, "rain": 480, "temp": 28.2, "hot_days": 124},
                {"year": 2013, "rain": 640, "temp": 27.7, "hot_days": 108},
                {"year": 2014, "rain": 590, "temp": 27.9, "hot_days": 115},
                {"year": 2015, "rain": 510, "temp": 28.4, "hot_days": 128},
                {"year": 2016, "rain": 530, "temp": 28.5, "hot_days": 130},
                {"year": 2017, "rain": 670, "temp": 27.6, "hot_days": 107},
                {"year": 2018, "rain": 580, "temp": 28.0, "hot_days": 116},
                {"year": 2019, "rain": 730, "temp": 27.3, "hot_days": 102},
                {"year": 2020, "rain": 710, "temp": 27.5, "hot_days": 106},
                {"year": 2021, "rain": 660, "temp": 27.8, "hot_days": 112},
                {"year": 2022, "rain": 680, "temp": 27.7, "hot_days": 109},
                {"year": 2023, "rain": 490, "temp": 28.6, "hot_days": 132},
                {"year": 2024, "rain": 620, "temp": 28.1, "hot_days": 118},
            ]
        }
    },
    "Mandya, Karnataka, India (Southern Dry Zone - Cauvery Basin)": {
        "lat": 12.5218,
        "lon": 76.8951,
        "climate_type": "Tropical semi-arid (Red sandy loams, Canal-irrigated command areas & rainfed uplands)",
        "default_past_crops": ["Finger Millet (Ragi)", "Groundnut (Peanut)"],
        "fallback_soil": {"clay_pct": 22.0, "sand_pct": 58.0, "soc_pct": 0.72, "ph": 6.5},
        "fallback_climate": {
            "mean_annual_rainfall_mm": 780.0,
            "rainfall_trend_pct": -1.8,
            "mean_annual_temp_c": 24.8,
            "warming_rate_c_decade": 0.24,
            "hot_days_per_year": 34,
            "dry_spells_per_year": 2.8,
            "annual_series": [
                {"year": 2010, "rain": 890, "temp": 24.4, "hot_days": 28},
                {"year": 2011, "rain": 760, "temp": 24.6, "hot_days": 32},
                {"year": 2012, "rain": 640, "temp": 25.1, "hot_days": 42},
                {"year": 2013, "rain": 810, "temp": 24.7, "hot_days": 30},
                {"year": 2014, "rain": 830, "temp": 24.8, "hot_days": 33},
                {"year": 2015, "rain": 710, "temp": 25.2, "hot_days": 44},
                {"year": 2016, "rain": 590, "temp": 25.4, "hot_days": 48},
                {"year": 2017, "rain": 870, "temp": 24.6, "hot_days": 31},
                {"year": 2018, "rain": 780, "temp": 24.9, "hot_days": 36},
                {"year": 2019, "rain": 850, "temp": 24.7, "hot_days": 32},
                {"year": 2020, "rain": 880, "temp": 24.5, "hot_days": 29},
                {"year": 2021, "rain": 940, "temp": 24.6, "hot_days": 30},
                {"year": 2022, "rain": 910, "temp": 24.7, "hot_days": 32},
                {"year": 2023, "rain": 630, "temp": 25.5, "hot_days": 50},
                {"year": 2024, "rain": 800, "temp": 25.0, "hot_days": 38},
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
                {"year": 2021, "rain": 880, "temp": 8.8, "hot_days": 19},
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

def check_is_farmland(lat: float, lon: float, live_soil: dict = None) -> bool:
    if lat > 78.0 or lat < -58.0:
        return False
        
    if (-55.0 <= lat <= 55.0) and (-179.9 <= lon <= -128.0):
        if not (18.0 <= lat <= 23.0 and -161.0 <= lon <= -154.0):
            return False
    if (-50.0 <= lat <= 40.0) and (155.0 <= lon <= 180.0):
        if not (-48.0 <= lat <= -34.0 and 165.0 <= lon <= 179.0):
            return False
            
    if (-45.0 <= lat <= 60.0) and (-45.0 <= lon <= -18.0):
        if not (63.0 <= lat <= 67.0 and -25.0 <= lon <= -13.0):
            return False
            
    if (-50.0 <= lat <= 10.0) and (55.0 <= lon <= 95.0):
        if not (5.8 <= lat <= 10.0 and 79.5 <= lon <= 82.0):
            return False
            
    if live_soil is not None:
        if live_soil.get("soc_pct", 0) <= 0.0:
            return False

    return True
