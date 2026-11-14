# 🌾 FieldShift Rotation Advisor

**Adapting Farms with NASA Earth Observations & Local Soil Intelligence**  
*Developed for the NASA International Space Apps Challenge 2026*  
**Challenge:** *Field Shift: Adapting Farms with NASA Data*

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.37+-red.svg)](https://streamlit.io/)
[![NASA POWER](https://img.shields.io/badge/NASA%20Data-POWER%20Agroclimatology-0B3D91.svg)](https://power.larc.nasa.gov/)
[![ISRIC SoilGrids](https://img.shields.io/badge/Soil%20Data-ISRIC%20SoilGrids%20250m-green.svg)](https://soilgrids.org/)

---

## 🎯 Executive Summary & Problem Statement

Farmers worldwide face severe climate headwinds: shifting rainfall baselines, prolonged dry spells, extreme heat days during critical flowering windows, and depleting soil organic matter. In traditional monoculture or simple two-crop rotations (such as continuous corn or corn-soybean), these stresses lead to depleted aquifers, escalating fertilizer costs, compaction, and yield volatility.

**FieldShift Rotation Advisor** is an open-source, deterministic decision-support tool that connects NASA Earth observations and gridded soil intelligence with transparent agronomic science. It empowers farmers to evaluate 3-season crop rotation sequences tailored to their exact location, field history, and strategic priorities (water savings, soil health, economic stability, or climate resilience).

---

## 🛰️ How NASA Data is Used

FieldShift connects directly to the **NASA Prediction Of Worldwide Energy Resources (POWER) Agroclimatology API**:
- **Dataset:** Daily point meteorological records (15-year historical horizon, 2010–2024).
- **Core Parameters:**
  - `PRECTOTCORR`: Bias-corrected precipitation (calculating annual rainfall normals, decadal rainfall trend, and dry-spell frequency >14 consecutive rain-free days).
  - `T2M`: Daily 2-meter air temperature (calculating long-term warming trajectory and degree-day trends).
  - `T2M_MAX`: Maximum daily temperature (identifying frequency of extreme heat stress days >35°C during crop reproductive stages).
- **Data Provenance:** NASA Langley Research Center POWER Project (`https://power.larc.nasa.gov/api/temporal/daily/point`, Community: `AG`).

---

## 🧪 Local Soil Data Integration

- **ISRIC SoilGrids 250m REST API v2.0:** Integrates physical and chemical soil properties across the 0–30 cm root-zone profile:
  - Clay & Sand fractions (% texture) to determine water-holding capacity and drainage class.
  - Soil Organic Carbon (SOC %) to baseline biological soil health and fertility potential.
  - Soil pH ($H_2O$) to screen crop acid/alkaline tolerances.
- **Farmer Lab Test Override:** Farmers can enter their own certified soil test values directly in the sidebar for customized field diagnostics.

---

## ⚙️ Agronomic Knowledge Base & Rotation Engine

FieldShift embeds an FAO-grounded crop database (`crops.csv`) containing 8 foundational food, feed, and cover crops:
- Maize (*Zea mays*), Soybean (*Glycine max*), Winter Wheat (*Triticum aestivum*), Grain Sorghum (*Sorghum bicolor*), Chickpea (*Cicer arietinum*), Alfalfa (*Medicago sativa*), Sunflower (*Helianthus annuus*), and Multi-Species Cover Crop (Clover-Rye mix).

### Agronomic Decision Rules:
1. **Botanical Family Pest-Break Rule:** Strictly prohibits planting the same botanical family back-to-back (e.g., Poaceae grass to Poaceae grass) to break nematode, weed, and fungal disease cycles.
2. **Biological Nitrogen Fixation Rule:** Mandates the inclusion of at least one nitrogen-fixing legume (*Fabaceae*) or legume cover crop within the 3-year cycle, directly cutting synthetic fertilizer dependency and greenhouse gas emissions.
3. **Root Architecture Synergy:** Rewards the strategic pairing of fibrous-rooted crops with deep taproot species (e.g., Sunflower or Alfalfa reaching 1.8–2.5m) to naturally bio-drill through compacted plow pans and scavenge subsoil moisture.
4. **Hydrological Feasibility:** Computes cumulative seasonal water demand against the 15-year NASA precipitation envelope to safeguard against groundwater overdraft.

---

## 🚀 Quickstart & Local Installation

### Prerequisites
- Python 3.10, 3.11, or 3.12
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/fieldshift-rotation-advisor.git
cd fieldshift-rotation-advisor
```

### 2. Create and Activate a Virtual Environment
```bash
# On Windows
python -m venv .venv
.venv\Scripts\activate

# On macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Streamlit Application
```bash
streamlit run app.py
```
Open `http://localhost:8501` in your web browser.

---

## 📁 Repository Structure

```
FieldShift/
├── app.py                # Main Streamlit web application & scoring engine
├── crops.csv             # FAO-grounded crop agronomic database
├── requirements.txt      # Core Python dependencies
├── .gitignore            # Git exclusion rules
└── README.md             # Project documentation, architecture & pitch
```

---

## 📚 References & Scientific Sources

1. **NASA POWER Project:** Daily Agroclimatology Data Archive, NASA Langley Research Center. API: `https://power.larc.nasa.gov/api/temporal/daily/point`.
2. **ISRIC SoilGrids 250m:** Poggio et al. (2021). *SoilGrids 2.0: producing soil property maps with Python and machine learning*. SOIL, 7, 217–240. API: `https://rest.isric.org/soilgrids/v2.0/properties/query`.
3. **FAO Irrigation & Drainage Paper No. 56:** Allen, R. G., Pereira, L. S., Raes, D., & Smith, M. (1998). *Crop evapotranspiration - Guidelines for computing crop water requirements*. Food and Agriculture Organization of the United Nations, Rome.
4. **FAO Irrigation & Drainage Paper No. 33:** Doorenbos, J., & Kassam, A. H. (1979). *Yield response to water*. FAO, Rome.
5. **FAO EcoCrop & Soil Bulletin 80:** Biological Nitrogen Fixation, soil cover management, and crop ecological requirements.

---

## 🏆 NASA Space Apps Challenge 2026 Submission Note
- **Hackathon:** NASA International Space Apps Challenge 2026 (Nov 14–15, 2026)
- **Challenge Track:** *Field Shift: Adapting Farms with NASA Data*
- **License:** Open Source under the MIT License.
