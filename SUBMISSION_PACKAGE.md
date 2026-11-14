# 🚀 NASA Space Apps Challenge 2026: Official Submission Package

**Project Title:** FieldShift Rotation Advisor  
**Challenge:** Field Shift: Adapting Farms with NASA Data  
**Repository:** [Public GitHub Repository Link]  
**Live Demo:** [Streamlit Community Cloud Link]

---

## 1. Short Project Summary (High-Impact Elevator Pitch)
*Word count: ~100 words*

Across the globe, farmers face shifting rainfall baselines, groundwater depletion, intensifying heatwaves, and declining soil organic matter. Traditional monocultures and rigid rotations exacerbate these vulnerabilities. **FieldShift Rotation Advisor** is an open-source agronomic decision-support platform that transforms 15 years of NASA Earth observations (POWER Agroclimatology) and global soil intelligence (ISRIC SoilGrids) into personalized, scientifically validated 3-season crop rotation strategies. By evaluating water budgets, root-zone architecture, biological nitrogen fixation, and pest-break cycles against farmer priorities, FieldShift empowers growers to conserve critical water, restore soil vitality, and build lasting climate resilience.

---

## 2. Detailed Project Description
*Comprehensive narrative covering Problem, Solution, and Agronomic Science*

### The Problem
Agricultural communities are on the frontlines of climate volatility. Famers frequently encounter:
1. **Unpredictable Precipitation & Dry Spells:** Historical rainfall patterns no longer match traditional crop calendars, causing severe drought stress or groundwater overdraft.
2. **Extreme Heat Spikes:** Heatwaves exceeding critical crop physiological thresholds (>35°C) during anthesis/flowering destroy yield potential.
3. **Soil Degradation & Compaction:** Decades of continuous cereal monocultures or repetitive rotations have depleted soil organic carbon (SOC) and created impenetrable plow pans that prevent water infiltration.

### The Solution: FieldShift Rotation Advisor
FieldShift bridges satellite Earth observation science and practical on-farm decisions through a lean, accessible web application.
- **Location-Specific Agroclimatic Diagnostics:** Farmers select their location or choose benchmark farms (e.g., semi-arid High Plains vs. humid Corn Belt). FieldShift queries 15 years of daily NASA satellite and assimilation data to quantify annual rainfall normals, decadal precipitation trends, warming rates, and extreme heat days.
- **Root-Zone Soil Characterization:** Integrated 0–30 cm soil horizons from ISRIC SoilGrids reveal texture (clay/sand) and soil organic carbon, with an optional field-lab test override for precision management.
- **Agronomic Rule Engine & Deterministic Scoring:** Evaluates candidate multi-season rotation combinations under strict FAO agronomic principles:
  - *Pest Break:* Enforces botanical family rotation (e.g., Poaceae to Fabaceae) to halt pathogen cycles.
  - *Fertility Restoration:* Mandates nitrogen-fixing legumes to restore organic carbon and reduce synthetic fertilizer dependency.
  - *Bio-Drilling:* Combines fibrous shallow root systems with deep taproots (e.g., Sunflower/Alfalfa reaching 1.8–2.5m) to alleviate soil compaction naturally.
  - *Water Envelope:* Matches cumulative rotation water requirements against historical NASA precipitation envelopes.
- **Transparent Benchmarking:** Ranks the top 3 rotation strategies against the farmer's current practice, providing explainable trade-off radar charts, water balance visualizers, and plain-language agronomic rationales.

---

## 3. NASA Earth Observations & Data Sources Used
*Strictly authentic, verified data sources implemented in the solution*

1. **NASA POWER (Prediction Of Worldwide Energy Resources) Agroclimatology API:**
   - **Source:** NASA Langley Research Center.
   - **Endpoint:** `https://power.larc.nasa.gov/api/temporal/daily/point` (Community: `AG`).
   - **Observed Parameters:**
     - `PRECTOTCORR`: Corrected daily precipitation (mm/day) — used to compute 15-year annual rainfall baselines, dry spell frequency (>14 consecutive rain-free days), and decadal precipitation trajectory.
     - `T2M`: Daily 2-meter air temperature (°C) — used to calculate long-term warming trends and thermal regimes.
     - `T2M_MAX`: Daily maximum 2-meter air temperature (°C) — used to detect frequency of extreme heat stress events (>35°C).

2. **ISRIC SoilGrids 250m REST API v2.0:**
   - **Source:** International Soil Reference and Information Centre (Wageningen, Netherlands).
   - **Endpoint:** `https://rest.isric.org/soilgrids/v2.0/properties/query`.
   - **Parameters:** Clay content (g/kg), Sand content (g/kg), Soil Organic Carbon (dg/kg), and pH in $H_2O$ across 0–5cm, 5–15cm, and 15–30cm depths.

3. **FAO (Food and Agriculture Organization of the United Nations):**
   - **FAO Irrigation and Drainage Paper No. 56:** Crop evapotranspiration guidelines and crop water requirements ($ET_c$).
   - **FAO Irrigation and Drainage Paper No. 33:** Yield response to water stress.
   - **FAO EcoCrop Database & Soil Bulletin 80:** Botanical classification, rooting depth, pH limits, and biological nitrogen fixation capacities.

---

## 4. 30–60 Second Video Pitch Script

**[0:00 - 0:10] Hook & Problem:**  
*(Visual: Drought-cracked field or satellite climate map)*  
"Farmers everywhere are facing a climate paradox: shifting rainfall, sudden heatwaves, and exhausted soils. When traditional monocultures fail, how do farmers know what crop rotation will save their farm?"

**[0:10 - 0:25] Introducing FieldShift & NASA Data:**  
*(Visual: Screen capture of FieldShift app selecting location and showing NASA POWER charts)*  
"Meet **FieldShift Rotation Advisor**. By connecting directly to NASA's POWER satellite archive, FieldShift analyzes 15 years of daily rainfall trends, extreme heat events, and ISRIC soil properties for any field on Earth."

**[0:25 - 0:45] The Agronomic Engine in Action:**  
*(Visual: Moving sliders, showing the comparison table and radar chart)*  
"Farmers set their priorities—saving water, building soil organic matter, or hedging market risk. Our deterministic agronomic engine designs 3-season rotations that break pest cycles, integrate nitrogen-fixing legumes, and match crop water needs to actual NASA rainfall envelopes."

**[0:45 - 0:60] Impact & Vision:**  
*(Visual: Top rotation recommendation showing +35% water conservation and soil improvement)*  
"FieldShift gives farmers transparent, science-backed confidence to adapt their fields before disaster strikes. Adapting farms with NASA Earth observations. FieldShift: Smarter Rotations for a Changing World."

---

## 5. Live Pitch Outline (Judges Presentation Deck)

- **Slide 1: Title & Hook:** FieldShift Rotation Advisor — Adapting Farms with NASA Data (NASA Space Apps Challenge 2026).
- **Slide 2: The Grower's Dilemma:** Unprecedented weather extremes + soil degradation = economic and food security crises.
- **Slide 3: Why Status Quo Fails:** Monoculture locks farmers into escalating water pumping and synthetic nitrogen spirals.
- **Slide 4: NASA Earth Observation Pipeline:** Live integration of NASA POWER daily climate records (precipitation, temperature, heat spikes) + ISRIC SoilGrids.
- **Slide 5: The FieldShift Engine:** Strict agronomic laws: Botanical diversity, biological nitrogen fixation, and deep-root bio-drilling.
- **Slide 6: Live Comparison & Transparency:** Top 3 rotations benchmarked directly against continuous monoculture with zero "black-box" guessing.
- **Slide 7: Scalability & Next Steps:** Expansion to NASA SMAP (soil moisture active-passive) and MODIS/VIIRS NDVI real-time vegetative anomaly tracking.
- **Slide 8: Team & Open-Source Commitment:** Open repository, reproducible data pipelines, and free access for smallholder and commercial growers worldwide.
