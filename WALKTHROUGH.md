# 🚀 FieldShift: Platform Walkthrough & Judge Demonstration Guide

**NASA International Space Apps Challenge 2026**  
**Challenge:** *Field Shift: Adapting Farms with NASA Data*  
**Project:** FieldShift Multi-Page Decision Support Platform

---

## 🧭 5-Minute Evaluation Walkthrough

Follow this step-by-step route to inspect the full depth of FieldShift's Earth Observation and agronomic decision-support platform.

### Step 1: Tactical Mission Control (Page 1)
1. Launch the platform at `http://localhost:8501`.
2. Notice the top **Command Bar** showing live NASA POWER status and target telemetry.
3. Interact with the **Hero 3D Earth Cockpit**:
   - Rotate the Earth in real-time with left-click drag.
   - Adjust altitude with the mouse wheel.
   - Toggle `ORBIT VIEW`, `FIELD VIEW`, and `NIGHT VIS` mode.
   - Center over an agricultural region and click `🎯 LOCK TARGET` inside the cockpit. The coordinates instantly update across the entire platform.
4. Select `Hubballi-Dharwad, Karnataka, India` from the Benchmark Sector dropdown.
5. Inspect Module 01: 15-year NASA POWER climate trends (precipitation trend, warming rate, extreme heat exposure days >35°C) and ISRIC SoilGrids 0-30cm soil texture fractions.
6. Review Module 02: Top 3 ranked rotation strategies scored against the status quo monoculture, showing water conservation, biological nitrogen fixation, and family diversity.
7. Switch to Tab `03 // SENSOR MAP & SOIL`:
   - Toggle between NASA GIBS satellite raster layers: *True Color*, *MODIS 16-Day NDVI*, *GPM Daily Precipitation*, and *SMAP Soil Moisture*.
   - Adjust the Opacity Slider.
   - Inspect the **Parcel Geodesic Telemetry** card showing centroid, calculated acreage (e.g. 794.6 acres), and perimeter.

### Step 2: Climate Scenario Simulator (Page 2)
1. Click `CLIMATE SIMULATOR` in the sidebar under `TACTICAL PLATFORM`.
2. Select the preset `Moderate Drought & Warming (+1.5°C, -20% Rain)` or drag the anomaly sliders.
3. Inspect Module 01: Real-time calculation of altered annual rainfall, warming trajectory, extreme heat days, and the **FAO-56 Hargreaves-Samani Reference Evapotranspiration ($ET_0$)** water balance.
4. Expand the calculation method to review the mathematical formula:
   $$ET_0 = 0.0023 \times R_a \times (T_{mean} + 17.8) \times \sqrt{T_{max} - T_{min}}$$
5. Inspect Module 02: Side-by-side re-scoring of rotation sequences under climate stress, highlighting unmet water deficits and score shifts.

### Step 3: 3D Farm Digital Twin (Page 3)
1. Click `3D DIGITAL TWIN` in the sidebar.
2. Observe the procedural Three.js WebGL agricultural canopy rendered using `InstancedMesh` for 60fps performance.
3. Use the sidebar controls:
   - Switch active crops (e.g. *Chickpea*, *Grain Sorghum*, *Finger Millet (Ragi)*).
   - Drag the **Phenological Growth Stage Slider** from Stage 0 (Sown Furrow) to Stage 3 (Flowering) and Stage 5 (Maturity). Notice the canopy height and foliage density adapt dynamically.
   - Toggle **Atmospheric Environment** between *Summer*, *Monsoon*, *Post-Monsoon*, and *Winter*.
   - Toggle **Subterranean Soil Cutaway**: observe the stratigraphic horizons (Topsoil 0-30cm, Subsoil 30-100cm), root architecture reaching the exact rooting depth from `crops.csv`, and animated pore-water infiltration droplets!

### Step 4: AI Agronomist (Page 4)
1. Click `AI AGRONOMIST` in the sidebar.
2. Notice the engine status: operates with live Google Gemini 2.5 Flash when an API key is provided, or seamlessly with the deterministic FAO-56 rule-based engine when offline.
3. Click any of the quick inquiry chips:
   - `🌱 Why is this rotation recommended?`
   - `🌡️ How does extreme heat affect this field?`
   - `🧪 How can I improve soil organic carbon?`
4. Inspect the generated response: notice the exact grounding in the active farm's NASA POWER indicators and ISRIC soil texture, along with explicit provenance tags and anti-hallucination disclaimers.
5. Expand `🔍 View Grounded Farm Context Payload Sent to AI` to verify the clean, transparent JSON pipeline.

### Step 5: Farm Report & Dossier (Page 5)
1. Click `FARM REPORT` in the sidebar under `ANALYSIS & GOVERNANCE`.
2. Inspect the executive farm dossier with standardized scientific provenance chips (`LIVE API`, `DERIVED`, `MODELED`, `APPROXIMATE TABLE`).
3. Click `📥 DOWNLOAD AUDIT-READY PDF DOSSIER`: generates a publication-grade multi-page PDF using pure Python ReportLab, complete with embedded 15-year NASA climate charts.
4. Download the structured CSV and JSON exports.
5. Review the **15-Core Composite Soil Sampling Planner** with physical and chemical protocol checklists.

### Step 6: Scientific Methodology & Provenance Registry (Page 6)
1. Click `METHODOLOGY & DATA` in the sidebar.
2. Review the complete open-science architecture:
   - Source Provenance Registry with spatial/temporal resolutions and official API endpoints.
   - LaTeX mathematical formulations for Climate Indicators, FAO-56 Reference $ET_0$, and Rotation Scoring.
   - Crop parameter citation table detailing FAO Irrigation & Drainage Papers No. 56 & 33 and ICRISAT.
   - Step-by-step worked numerical calculation example.
   - Full disclosure of scientific limitations.

---
*FieldShift Platform — NASA Space Apps Challenge 2026*
