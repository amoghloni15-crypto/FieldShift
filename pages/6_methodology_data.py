"""
FieldShift Scientific Methodology & Data Registry (Page 6).
Exhaustive transparency registry covering data sources, mathematical indicator formulas,
crop agronomic basis, rotation scoring equations, and scientific limitations.
"""

import streamlit as st
import pandas as pd
from core.ui_theme import (
    render_html, inject_vault_styles, render_command_bar, render_provenance_badge,
    render_error_boundary, fmt_num
)
from core.agronomy_engine import load_crop_database

inject_vault_styles()

render_command_bar(
    "SCIENTIFIC METHODOLOGY & DATA REGISTRY",
    "TRANSPARENT ALGORITHMIC ARCHITECTURE • OPEN SCIENCE DECISION SUPPORT"
)

# SECTION 1: DATA SOURCES REGISTRY
render_html('<div class="module-header">01 // SCIENTIFIC DATA PROVENANCE REGISTRY</div>')

registry_data = [
    {
        "Data Source": "NASA POWER Agroclimatology",
        "Provider": "NASA Langley Research Center",
        "Parameters": "T2M (Mean Temp), T2M_MAX (Peak Temp), PRECTOTCORR (Precipitation)",
        "Spatial Resolution": "0.5° × 0.5° (~50 km)",
        "Temporal Resolution": "Daily records (15-yr horizon: 2010–2024)",
        "Access Method": "REST API (JSON point query)",
        "Auth / Key": "None (Public Domain)",
        "Provenance": "LIVE API"
    },
    {
        "Data Source": "ISRIC SoilGrids 250m v2.0",
        "Provider": "ISRIC – World Soil Information",
        "Parameters": "Clay %, Sand %, Soil Organic Carbon (SOC %), pH (H2O)",
        "Spatial Resolution": "250m gridded global map",
        "Temporal Resolution": "Static multi-depth profile (0–5cm, 5–15cm, 15–30cm)",
        "Access Method": "REST API (JSON point query)",
        "Auth / Key": "None (Open CC-BY 4.0)",
        "Provenance": "LIVE API"
    },
    {
        "Data Source": "NASA GIBS / ESDIS Worldview",
        "Provider": "NASA Earth Science Data & Information System",
        "Parameters": "MODIS Terra True-Color Corrected Reflectance & Blue Marble",
        "Spatial Resolution": "250m native satellite resolution (Level 9)",
        "Temporal Resolution": "Daily orbital composite (48-hr latency)",
        "Access Method": "WMTS REST Tile Protocol (EPSG:3857)",
        "Auth / Key": "None (Open Earth Observation)",
        "Provenance": "LIVE API"
    },
    {
        "Data Source": "FAO Grounded Crop Database",
        "Provider": "FAO Irrigation & Drainage Papers No. 56 & 33",
        "Parameters": "Seasonal water need (mm), Root depth (m), Family, N-fixation",
        "Spatial Resolution": "Species-level physiological guidelines",
        "Temporal Resolution": "Standard seasonal crop cycle",
        "Access Method": "Local CSV Database (crops.csv)",
        "Auth / Key": "None (Local Static File)",
        "Provenance": "APPROXIMATE TABLE"
    },
    {
        "Data Source": "Farmer Soil Lab Override",
        "Provider": "Participating Farmer / Local Soil Testing Laboratory",
        "Parameters": "Custom Clay %, Sand %, Organic Carbon %, pH",
        "Spatial Resolution": "Point field-level core sample",
        "Temporal Resolution": "Current season soil test",
        "Access Method": "Interactive Sidebar Input Widgets",
        "Auth / Key": "None (Direct User Input)",
        "Provenance": "FARMER INPUT"
    },
    {
        "Data Source": "Verified Regional Baseline Archive",
        "Provider": "FieldShift Embedded Benchmark Knowledgebase",
        "Parameters": "15-yr annual climate series and soil physical baselines",
        "Spatial Resolution": "7 representative global agro-ecological zones",
        "Temporal Resolution": "2010–2024 annual aggregates",
        "Access Method": "Embedded Python In-Memory Repository",
        "Auth / Key": "None (Local Verified Cache)",
        "Provenance": "FALLBACK DEMO DATA"
    }
]

df_registry = pd.DataFrame(registry_data)
st.dataframe(df_registry, use_container_width=True, hide_index=True)

# SECTION 2: MATHEMATICAL CLIMATE INDICATORS
render_html('<div class="module-header" style="margin-top: 25px;">02 // CLIMATE INDICATOR FORMULAS & CALCULATION LOGIC</div>')

render_html(r"""
<div class="holo-metric-card" style="margin-bottom: 16px;">
  <div style="font-family: 'Share Tech Mono', monospace; font-size: 0.95rem; color: #E8F6FF; line-height: 1.8;">
    <div><strong>1. Extreme Heat Days ($T_{max} > 35°C$):</strong> Count of days within each calendar year where peak 2-meter air temperature exceeds 35.0°C. 35°C is the recognized physiological threshold where pollen sterility and thermal shock occur in cereal reproductive stages (flowering/anthesis).</div>
    <div style="margin-top: 8px;"><strong>2. Consecutive Dry Spells ($>14\text{ days}$):</strong> An agroclimatic dry spell is recorded when consecutive precipitation remains strictly below 1.0 mm/day for 14 continuous days during the growing year.</div>
    <div style="margin-top: 8px;"><strong>3. Decadal Rainfall Trend ($\% / \text{decade}$):</strong> Ordinary Least Squares (OLS) linear slope ($\beta_{rain}$) fitted across 15 consecutive annual totals: 
    $$\text{Trend } (\%) = \left(\frac{\beta_{rain} \times 10}{\bar{P}}\right) \times 100$$</div>
    <div style="margin-top: 8px;"><strong>4. Decadal Warming Trajectory ($°C / \text{decade}$):</strong> OLS linear slope ($\beta_{temp}$) of mean annual 2-meter temperature multiplied by 10 years: 
    $$\Delta T_{decade} = \beta_{temp} \times 10$$</div>
  </div>
</div>
""")

# SECTION 3: CROP KNOWLEDGEBASE & APPROXIMATIONS
render_html('<div class="module-header" style="margin-top: 25px;">03 // CROP DATABASE & PARAMETRIC UNCERTAINTIES</div>')

crop_df = load_crop_database()
st.dataframe(crop_df, use_container_width=True, hide_index=True)

render_html("""
<div style="font-family: 'Rajdhani', sans-serif; font-size: 0.95rem; color: #8FA6B8; line-height: 1.6; margin-top: 8px;">
  <strong style="color: #FF9E1F;">PARAMETRIC DISCLOSURE:</strong> Crop water requirements ($ET_c$ mm) and rooting depths ($m$) are <strong>generalized species-level approximations</strong> 
  derived from FAO Irrigation and Drainage Paper No. 56 and No. 33. Actual field water demand fluctuates based on atmospheric vapor pressure deficit ($VPD$), solar irradiance, planting density, and crop variety.
</div>
""")

# SECTION 4: ROTATION RULES & SCORING EQUATION
render_html('<div class="module-header" style="margin-top: 25px;">04 // ROTATION ELIGIBILITY RULES & MULTI-CRITERIA SCORING</div>')

render_html("""
<div class="rotation-hero-card">
  <div class="rank-badge gold">DETERMINISTIC AGRONOMIC FILTERS</div>
  <div style="margin-top: 10px; font-family: 'Rajdhani', sans-serif; font-size: 1rem; color: #E8F6FF; line-height: 1.7;">
    <div><strong>Rule 1 — Botanical Pest Break:</strong> Back-to-back planting of crops from the same botanical family (e.g. <em>Poaceae</em> grass after <em>Poaceae</em> grass) is strictly forbidden. This interrupts nematode reproduction, root rot fungal cycles, and host-specific insect proliferation.</div>
    <div><strong>Rule 2 — Nitrogen Fixation Requirement:</strong> Every 3-season rotation must include at least one biological nitrogen-fixing species from the <em>Fabaceae</em> family (e.g. Soybean, Chickpea, Alfalfa, or Clover).</div>
    <div><strong>Rule 3 — Monoculture Elimination:</strong> Three identical consecutive seasons ($C_1 = C_2 = C_3$) are immediately disqualified.</div>
  </div>
</div>
""")

render_html(r"""
<div class="rotation-hero-card" style="margin-top: 12px;">
  <div class="rank-badge cyan">COMPOSITE SCORING EQUATION</div>
  <div style="margin-top: 10px; font-family: 'Share Tech Mono', monospace; font-size: 0.95rem; color: #E8F6FF; line-height: 1.8;">
    <div>$$\text{Composite Score} = \frac{W_{water} \cdot S_{water} + W_{soil} \cdot S_{soil} + W_{econ} \cdot S_{econ} + W_{resil} \cdot S_{resilience}}{\sum W} - P_{pH}$$</div>
    <div style="margin-top: 6px; font-size: 0.85rem; color: #8FA6B8;">
      Where $S_{water}$ evaluates cumulative crop evapotranspiration against NASA historical rainfall normals;<br/>
      $S_{soil}$ evaluates organic residue cover, deep taproot aeration ($>1.5\text{m}$), and family biodiversity bonus;<br/>
      $S_{econ}$ incorporates market volatility penalties;<br/>
      $S_{resilience}$ evaluates C4 heat and drought tolerance against annual heat stress days ($>35°C$);<br/>
      $P_{pH}$ applies an 8-point penalty per species exceeding soil pH tolerance boundaries.
    </div>
  </div>
</div>
""")

# SECTION 5: WORKED NUMERICAL EXAMPLE
render_html('<div class="module-header" style="margin-top: 25px;">05 // WORKED NUMERICAL EXAMPLE (CURRENT FARM CONFIGURATION)</div>')

if st.session_state.get("analysis_completed") and st.session_state.get("top_rotations"):
    try:
        r1 = st.session_state["top_rotations"][0]
        weights = st.session_state["priority_weights"]
        c_data = st.session_state["climate_data"]
        s_data = st.session_state["soil_data"]
        
        seq_str = " ➔ ".join(r1.get("crops", []))
        w_tot = sum(weights.values())
        calc_score = (weights.get('water', 3)*r1.get('s_water', 50) + weights.get('soil', 3)*r1.get('s_soil', 50) + weights.get('econ', 3)*r1.get('s_econ', 50) + weights.get('resilience', 3)*r1.get('s_resilience', 50)) / max(w_tot, 1)

        render_html(f"""
        <div class="holo-metric-card">
          <div style="font-family: 'Orbitron', monospace; font-size: 1.1rem; color: #19F3FF;">RANK #1 CANDIDATE: {seq_str}</div>
          <div style="margin-top: 8px; font-family: 'Share Tech Mono', monospace; font-size: 0.9rem; color: #E8F6FF; line-height: 1.8;">
            <div>• Water Score ($S_{{water}}$): <strong>{fmt_num(r1.get('s_water'), 1)}</strong> | Weight: <strong>{weights.get('water', 3)}</strong> ➔ Contribution: {fmt_num(weights.get('water', 3) * float(r1.get('s_water', 0)), 1)}</div>
            <div>• Soil Health Score ($S_{{soil}}$): <strong>{fmt_num(r1.get('s_soil'), 1)}</strong> | Weight: <strong>{weights.get('soil', 3)}</strong> ➔ Contribution: {fmt_num(weights.get('soil', 3) * float(r1.get('s_soil', 0)), 1)}</div>
            <div>• Market Score ($S_{{econ}}$): <strong>{fmt_num(r1.get('s_econ'), 1)}</strong> | Weight: <strong>{weights.get('econ', 3)}</strong> ➔ Contribution: {fmt_num(weights.get('econ', 3) * float(r1.get('s_econ', 0)), 1)}</div>
            <div>• Resilience Score ($S_{{resilience}}$): <strong>{fmt_num(r1.get('s_resilience'), 1)}</strong> | Weight: <strong>{weights.get('resilience', 3)}</strong> ➔ Contribution: {fmt_num(weights.get('resilience', 3) * float(r1.get('s_resilience', 0)), 1)}</div>
            <div style="border-top: 1px solid rgba(25, 243, 255, 0.3); margin-top: 6px; padding-top: 6px; color: #2CFFB0;">
              Weighted Sum = {fmt_num(calc_score * w_tot, 1)} ÷ {w_tot} = <strong>{fmt_num(r1.get('composite_score'), 1)}/100</strong>
            </div>
          </div>
        </div>
        """)
    except Exception as e:
        render_error_boundary("Worked Calculation Engine", e)
else:
    render_html("""<div style="font-family: 'Share Tech Mono', monospace; color: #8FA6B8;">Execute an analysis on Mission Control to see the real-time worked calculation for your farm.</div>""")

# SECTION 6: SCIENTIFIC LIMITATIONS
render_html('<div class="module-header" style="margin-top: 25px;">06 // SCIENTIFIC LIMITATIONS & GROUND VALIDATION BOUNDARIES</div>')

render_html("""
<div class="holo-metric-card">
  <div style="font-family: 'Rajdhani', sans-serif; font-size: 1rem; color: #E8F6FF; line-height: 1.8;">
    <div>1. <strong>Coarse Spatial Scale:</strong> NASA POWER reanalysis data is gridded at 0.5° resolution (~50 km). Microclimates, rain shadows, and valley frost pockets may diverge from gridded reanalysis values.</div>
    <div>2. <strong>Gridded Soil Modeling:</strong> ISRIC SoilGrids 250m is a predictive statistical model generated from global soil profiles. It does not reflect recent farm management practices such as deep tillage, lime amendments, or heavy manure applications.</div>
    <div>3. <strong>Decision Support Boundary:</strong> FieldShift is designed for strategic horizon planning and relative risk reduction. It is <strong>not a yield prediction model</strong> or a guarantee of commercial crop profitability.</div>
    <div>4. <strong>Independent Field Verification:</strong> Farmers must always confirm seed availability, herbicide compatibility, and local agronomic practices with regional university extension specialists or certified crop advisors before planting.</div>
  </div>
</div>
""")
