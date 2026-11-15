"""
FieldShift Tactical Farm Report & Export Center (Page 5).
Generates ReportLab PDF Dossier, CSV, JSON, and On-Farm Soil Sampling Planner.
"""

import streamlit as st
import pandas as pd
from core.ui_theme import (
    render_html, inject_vault_styles, render_command_bar,
    render_provenance_badge, render_empty_analysis_notice,
    render_error_boundary, fmt_num
)
from core.report_generator import (
    generate_pdf_report, generate_csv_export, generate_json_export
)

inject_vault_styles()

render_command_bar(
    "FARM DOSSIER & EXPORT CENTER",
    "TACTICAL AGRONOMIC REPORTING • MULTI-FORMAT SCIENTIFIC DISCLOSURE"
)

if not st.session_state.get("analysis_completed"):
    render_empty_analysis_notice()
    if st.button("🚀 NAVIGATE TO MISSION CONTROL", use_container_width=True):
        st.switch_page("pages/1_mission_control.py")
else:
    farm_name = st.session_state.get("farm_name", "Unknown Sector")
    coords = st.session_state.get("coords", (33.5779, -101.8552))
    climate_type = st.session_state.get("climate_type", "Arable Continental")
    climate_data = st.session_state.get("climate_data", {})
    soil_data = st.session_state.get("soil_data", {})
    past_crops = st.session_state.get("past_crops", ["Maize (Corn)", "Soybean"])
    weights = st.session_state.get("priority_weights", {"water": 4, "soil": 5, "econ": 3, "resilience": 4})
    rotations = st.session_state.get("top_rotations", [])
    baseline = st.session_state.get("baseline_monoculture", {})
    active_scenario = st.session_state.get("active_scenario", None)

    try:
        # Executive Summary Card
        soil_badge = render_provenance_badge(soil_data.get("provenance", "LIVE API"), "0-30cm Depth")
        climate_badge = render_provenance_badge(climate_data.get("provenance", "LIVE API"), "NASA POWER 2010-2024")
        model_badge = render_provenance_badge("MODELED / SIMULATED", "FAO Rotation Rules")

        render_html(f"""
        <div class="holo-metric-card" style="margin-bottom: 20px;">
          <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 10px;">
            <div>
              <div class="holo-label">SELECTED FIELD SECTOR</div>
              <div style="font-family: 'Orbitron', monospace; font-size: 1.5rem; font-weight: 800; color: #FFFFFF; margin: 4px 0;">{farm_name}</div>
              <div style="font-family: 'Share Tech Mono', monospace; font-size: 0.9rem; color: #19F3FF;">COORDINATES: {coords[0]:+.4f}°N, {coords[1]:+.4f}°E • {climate_type}</div>
            </div>
            <div style="display: flex; flex-direction: column; gap: 6px; align-items: flex-end;">
              {climate_badge}
              {soil_badge}
              {model_badge}
            </div>
          </div>
          <div style="margin-top: 14px; padding-top: 12px; border-top: 1px solid rgba(25, 243, 255, 0.2); font-family: 'Rajdhani', sans-serif; font-size: 1rem; color: #E8F6FF; line-height: 1.6;">
            Cropping History: <strong>{past_crops[0]} (Season -2) ➔ {past_crops[1]} (Season -1)</strong> | Continuous Practice Score: <strong>{baseline.get('composite_score', 'N/A')}/100</strong>.<br/>
            Optimal Strategy: <strong>{' ➔ '.join(rotations[0]['crops']) if rotations else 'N/A'}</strong> (Score: <strong>{rotations[0]['composite_score'] if rotations else 'N/A'}/100</strong>).
          </div>
        </div>
        """)

        # Download Buttons Panel
        render_html('<div class="module-header">// DOWNLOADABLE TACTICAL DOSSIERS</div>')
        
        col_d1, col_d2, col_d3 = st.columns(3)
        
        with col_d1:
            pdf_bytes = generate_pdf_report(
                farm_name=farm_name,
                coords=coords,
                climate_type=climate_type,
                climate_data=climate_data,
                soil_data=soil_data,
                past_crops=past_crops,
                weights=weights,
                rotations=rotations,
                baseline_monoculture=baseline,
                active_scenario=active_scenario
            )
            st.download_button(
                label="📄 DOWNLOAD PDF DOSSIER",
                data=pdf_bytes,
                file_name=f"FieldShift_Dossier_{coords[0]:.2f}_{coords[1]:.2f}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            render_html("""<div style="font-family: 'Share Tech Mono', monospace; font-size: 0.75rem; color: #8FA6B8; text-align: center; margin-top: 4px;">ReportLab Pure-Python PDF • Embedded Matplotlib Climate Figures</div>""")

        with col_d2:
            csv_str = generate_csv_export(
                farm_name=farm_name,
                coords=coords,
                climate_data=climate_data,
                soil_data=soil_data,
                rotations=rotations
            )
            st.download_button(
                label="📊 DOWNLOAD CSV DATASET",
                data=csv_str.encode("utf-8"),
                file_name=f"FieldShift_Data_{coords[0]:.2f}_{coords[1]:.2f}.csv",
                mime="text/csv",
                use_container_width=True
            )
            render_html("""<div style="font-family: 'Share Tech Mono', monospace; font-size: 0.75rem; color: #8FA6B8; text-align: center; margin-top: 4px;">Normalized Tabular Dataset • Indicators & Rotation Alternatives</div>""")

        with col_d3:
            json_str = generate_json_export(
                farm_name=farm_name,
                coords=coords,
                climate_data=climate_data,
                soil_data=soil_data,
                past_crops=past_crops,
                weights=weights,
                rotations=rotations,
                baseline_monoculture=baseline,
                active_scenario=active_scenario
            )
            st.download_button(
                label="💾 DOWNLOAD JSON PAYLOAD",
                data=json_str.encode("utf-8"),
                file_name=f"FieldShift_Payload_{coords[0]:.2f}_{coords[1]:.2f}.json",
                mime="application/json",
                use_container_width=True
            )
            render_html("""<div style="font-family: 'Share Tech Mono', monospace; font-size: 0.75rem; color: #8FA6B8; text-align: center; margin-top: 4px;">Machine-Readable Schema • Provenance & Full Sequence Scores</div>""")

        # SOIL SAMPLING PLANNER
        render_html('<div class="module-header" style="margin-top: 30px;">02 // ON-FARM SOIL SAMPLING PLANNER (WHAT SATELLITES CANNOT MEASURE)</div>')
        
        render_html("""
        <div class="holo-metric-card" style="margin-bottom: 20px;">
          <div style="font-family: 'Orbitron', monospace; font-size: 1.05rem; font-weight: 700; color: #FF9E1F; letter-spacing: 1px;">
            ⚠️ SCIENTIFIC BOUNDARY DISCLOSURE
          </div>
          <div style="font-family: 'Rajdhani', sans-serif; font-size: 1rem; color: #E8F6FF; line-height: 1.6; margin-top: 6px;">
            Coarse satellite radiometers and global gridded machine-learning layers (like ISRIC SoilGrids 250m) are <strong>regional estimations</strong>. 
            Satellites cannot directly measure mobile plant-available chemical nutrients, plow pan depths, or subsoil biological activity. 
            Before investing in crop seeds or fertilizer programs, farmers must perform direct soil core sampling.
          </div>
        </div>
        """)

        col_s1, col_s2 = st.columns(2)
        with col_s1:
            render_html("""
            <div class="rotation-hero-card" style="height: 100%;">
              <div class="rank-badge gold">CRITICAL CHEMICAL MEASUREMENTS</div>
              <div style="margin-top: 12px; font-family: 'Share Tech Mono', monospace; font-size: 0.85rem; color: #E8F6FF; line-height: 1.8;">
                <div>• <strong style="color:#19F3FF;">Available Nitrogen (NO3-N & NH4-N):</strong> Dynamic root-zone nitrogen fluxes require 0-30cm and 30-60cm core tests.</div>
                <div>• <strong style="color:#19F3FF;">Plant-Available Phosphorus (Bray-1 / Mehlich-3):</strong> Essential to calibrate legume root nodulation efficiency.</div>
                <div>• <strong style="color:#19F3FF;">Exchangeable Potassium (K) & Magnesium (Mg):</strong> Regulates crop stomatal closure during summer heat waves.</div>
                <div>• <strong style="color:#19F3FF;">Micronutrients (Zinc, Iron, Boron):</strong> Trace minerals that determine reproductive flowering viability.</div>
                <div>• <strong style="color:#19F3FF;">Electrical Conductivity (ECe):</strong> Measures soil salinity build-up from groundwater irrigation.</div>
              </div>
            </div>
            """)

        with col_s2:
            render_html("""
            <div class="rotation-hero-card" style="height: 100%;">
              <div class="rank-badge cyan">PHYSICAL & BIOLOGICAL STRUCTURE</div>
              <div style="margin-top: 12px; font-family: 'Share Tech Mono', monospace; font-size: 0.85rem; color: #E8F6FF; line-height: 1.8;">
                <div>• <strong style="color:#2CFFB0;">Hardpan Compaction Depth:</strong> Penetrometer resistance checks (>2.0 MPa limits root elongation).</div>
                <div>• <strong style="color:#2CFFB0;">Bulk Density (g/cm³):</strong> Core cylinder ring tests to measure real pore volume and root aeration.</div>
                <div>• <strong style="color:#2CFFB0;">Field Saturated Hydraulic Conductivity (Ksat):</strong> Direct infiltration ring tests for water percolation.</div>
                <div>• <strong style="color:#2CFFB0;">Active Biological Carbon / Respiration:</strong> Evaluates living soil microbial biomass buffering nutrient cycling.</div>
                <div>• <strong style="color:#2CFFB0;">Effective Rooting Depth:</strong> Visual inspection of subsoil barriers (caliche, rock, gleyed clay).</div>
              </div>
            </div>
            """)

        # LOCAL VALIDATION CHECKLIST
        render_html('<div class="module-header" style="margin-top: 30px;">03 // LOCAL AGRONOMIC VALIDATION CHECKLIST</div>')
        render_html("""
        <div class="holo-metric-card">
          <div style="font-family: 'Rajdhani', sans-serif; font-size: 1.05rem; color: #E8F6FF; line-height: 1.8;">
            <div>☑ <strong>1. Consult Local Extension:</strong> Review proposed rotation sequences with your regional university agricultural extension agent or certified crop advisor (CCA).</div>
            <div>☑ <strong>2. Confirm Market Liquidity:</strong> Verify local elevator acceptance, transport distance, and storage infrastructure for recommended alternative crops (e.g. Grain Sorghum, Chickpea, Sunflower).</div>
            <div>☑ <strong>3. Verify Herbicide Carryover:</strong> Inspect previous season chemical application logs to ensure no residual herbicide inhibits subsequent sensitive broadleaf or grass seedlings.</div>
            <div>☑ <strong>4. Equipment Compatibility:</strong> Confirm planter seed plates, combine headers, and drying capacity match the physical grain requirements of the selected species.</div>
            <div>☑ <strong>5. Inoculant Verification:</strong> When planting legumes (Soybean, Chickpea, Alfalfa), ensure seed is properly coated with species-specific <em>Rhizobium</em> bacterial inoculant.</div>
          </div>
        </div>
        """)
    except Exception as e:
        render_error_boundary("Farm Dossier & Export Center", e)
