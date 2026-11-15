# 🌾 FieldShift: Planetary Farm Adaptation Platform

**Adapting Agriculture with NASA Earth Observations & Local Soil Intelligence**  
*Built for the NASA International Space Apps Challenge 2026*  
**Challenge:** *Field Shift: Adapting Farms with NASA Data*

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.37+-red.svg)](https://streamlit.io/)
[![NASA POWER](https://img.shields.io/badge/NASA%20Data-POWER%20Agroclimatology-0B3D91.svg)](https://power.larc.nasa.gov/)
[![ISRIC SoilGrids](https://img.shields.io/badge/Soil%20Data-ISRIC%20SoilGrids%20250m-green.svg)](https://soilgrids.org/)
[![Three.js](https://img.shields.io/badge/WebGL-Three.js%20r128-black.svg)](https://threejs.org/)
[![Google GenAI](https://img.shields.io/badge/AI-Google%20Gemini%202.5%20Flash-4285F4.svg)](https://ai.google.dev/)

---

## 🎯 Executive Summary & Platform Architecture

Farmers worldwide face severe climate headwinds: shifting precipitation envelopes, delayed monsoon onsets, prolonged dry spells, extreme reproductive heat during flowering (>35°C), and degrading soil organic carbon. In continuous monocultures or rigid two-crop rotations, these pressures lead to aquifer depletion, escalating synthetic nitrogen costs, and catastrophic yield volatility.

**FieldShift** is an open-source, multi-page tactical agroecological platform that operationalizes NASA Earth Observations, ISRIC global gridded soil stratigraphy, FAO-56 irrigation models, and Google Gemini AI into an interactive decision-support cockpit.

The platform is organized into two tactical tiers across 6 coordinated modules:
- **TACTICAL PLATFORM:**
  - `01 // MISSION CONTROL`: Hero 3D Earth Cockpit with bidirectional target locking (`declare_component`), lightsaber sliders, 15-year NASA POWER daily agroclimatology reanalysis, multi-objective rotation scoring, and NASA GIBS satellite recon.
  - `02 // CLIMATE SIMULATOR`: Parametric what-if stress testing (temperature anomaly, rainfall shifts, irrigation caps, monsoon lag) with FAO-56 Hargreaves-Samani reference evapotranspiration ($ET_0$) water balance and side-by-side resilience re-scoring.
  - `03 // 3D DIGITAL TWIN`: Procedural WebGL canopy and subterranean soil cutaway powered by Three.js (`InstancedMesh`), dynamic soil texture coloring, FAO rooting depths, 6 growth stages, 4 seasonal lighting environments, and animated pore-water infiltration droplets.
  - `04 // AI AGRONOMIST`: Grounded decision support powered by the official Google GenAI SDK (`google-genai`), passing compact structured JSON farm telemetry into Gemini 2.5 Flash, with strict anti-hallucination guardrails, multi-lingual support (English, Hindi, Kannada, Spanish), and a deterministic FAO rule-based fallback when offline.
- **ANALYSIS & GOVERNANCE:**
  - `05 // FARM REPORT & DOSSIER`: Instant pure-Python PDF report generation via ReportLab (with embedded Matplotlib 15-year climate charts), CSV sequence tables, JSON API payloads, an interactive 15-core Soil Sampling Planner, and a local validation checklist.
  - `06 // METHODOLOGY & DATA`: Comprehensive open-science provenance registry, mathematical equations (rotation composite score, Hargreaves $ET_0$, heat vulnerability), crop parameter citations, worked numerical example, and explicit scientific limitations.

---

## 🛰️ NASA Earth Observations & Data Pipeline

FieldShift connects directly to official NASA Earth Science APIs:
1. **NASA POWER Agroclimatology API** (`power.larc.nasa.gov`):
   - Streams 15 years (2010–2024) of daily reanalysis (~50 km resolution) for any global coordinate:
     - `PRECTOTCORR`: Daily bias-corrected precipitation (annual normals, decadal trend slope, and dry spells >14 days).
     - `T2M`: Mean 2-meter air temperature and decadal warming rate.
     - `T2M_MAX`: Daily maximum temperature (tracking frequency of extreme heat days >35°C during anthesis).
2. **NASA GIBS WMTS Satellite Telemetry** (`gibs.earthdata.nasa.gov`):
   - Multi-layer raster satellite recon in Web Mercator (EPSG:3857):
     - `MODIS Terra True Color`: Corrected reflectance (250m daily optical).
     - `MODIS Terra 16-Day NDVI`: Normalized Difference Vegetation Index (250m composite).
     - `GPM IMERG Daily Precipitation Rate`: Global Precipitation Measurement (~10km).
     - `SMAP L3 Surface Soil Moisture`: Soil Moisture Active Passive (9km enhanced dielectric).
     - `NASA Blue Marble`: Static global shaded relief topography (500m).
3. **ISRIC SoilGrids 250m v2.0 REST API** (`rest.isric.org`):
   - Physical and chemical soil properties across the 0–30 cm root-zone horizon: Clay %, Sand %, Soil Organic Carbon (SOC %), and Soil pH ($H_2O$), with manual farmer lab override support.

---

## 🌾 Crop Database & Regional Agrarian Presets

FieldShift embeds an expanded FAO-grounded crop database (`crops.csv`) containing 11 international and Indian regional crops:
- Maize (*Zea mays*), Soybean (*Glycine max*), Winter Wheat (*Triticum aestivum*), Grain Sorghum (*Sorghum bicolor*), Chickpea (*Cicer arietinum*), Alfalfa (*Medicago sativa*), Sunflower (*Helianthus annuus*), Multi-Species Cover Crop (Clover-Rye), Finger Millet / Ragi (*Eleusine coracana*), Pigeon Pea / Tur (*Cajanus cajan*), and Groundnut (*Arachis hypogaea*).

### Benchmark Agricultural Presets:
- **Lubbock, Texas, USA** (Semi-Arid High Plains, Ogallala Aquifer stress)
- **Hubballi-Dharwad, Karnataka, India** (Northern Transition Zone, Vertisol black cotton soil)
- **Raichur, Karnataka, India** (North Eastern Dry Zone, Tungabhadra basin)
- **Mandya, Karnataka, India** (Southern Dry Zone, Cauvery basin)
- **Ames, Iowa, USA** (Humid Corn Belt)
- **Ludhiana, Punjab, India** (Indo-Gangetic Plain)
- **Nakuru, Rift Valley, Kenya** (Equatorial Highland)
- **Sorriso, Mato Grosso, Brazil** (Cerrado Savanna)
- **Poltava, Ukraine** (Chernozem Steppe)
- **Dubbo, New South Wales, Australia** (Murray-Darling Basin)

---

## 🚀 Quickstart & Local Installation

### Prerequisites
- Python 3.10, 3.11, or 3.12
- Internet access for live NASA POWER and SoilGrids API calls (automatic cached fallback enabled if offline)

### Installation
```bash
# Clone the repository
git clone https://github.com/your-username/fieldshift.git
cd fieldshift

# Install dependencies
pip install -r requirements.txt

# Run the platform
streamlit run app.py
```

### Optional: Google Gemini API Key
To enable live AI Agronomist responses via Gemini 2.5 Flash:
1. Obtain a free API key from [Google AI Studio](https://aistudio.google.com/apikey).
2. Set it in `.streamlit/secrets.toml`:
   ```toml
   GEMINI_API_KEY = "your_actual_key_here"
   ```
   *(Or enter it directly in the AI Agronomist sidebar in the app).*

---

## 📜 Scientific Limitations & Provenance Disclaimer
- **Spatial Resolution:** NASA POWER (~50 km) and ISRIC SoilGrids (250m) represent regional reanalysis and digital soil mapping, not sub-meter field measurements.
- **Yield Claims:** FieldShift never claims exact metric tons per hectare or guarantees financial profits; recommendations represent relative resilience scores based on FAO crop coefficient tables.
- **Extension Validation:** All rotations should be validated with local county agricultural extension services and certified physical soil testing.
