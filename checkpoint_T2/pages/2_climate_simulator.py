"""
FieldShift Climate Scenario Simulator (Page 2).
Interactive What-If Sensitivity Modeling, FAO-56 Reference ET0 Water Balance,
and Real-Time Rotation Re-Scoring.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from core.ui_theme import (
    render_html, inject_vault_styles, render_command_bar,
    apply_vault_plotly_theme, render_arc_gauge, render_provenance_badge, render_empty_analysis_notice
)
from core.scenario_engine import (
    SCENARIO_PRESETS, apply_climate_scenario, rescore_rotations_under_scenario
)
from core.agronomy_engine import evaluate_baseline_monoculture

inject_vault_styles()

render_command_bar(
    "CLIMATE SCENARIO SIMULATOR",
    "WHAT-IF STRESS TESTING • HARMONIZED FAO-56 ET0 WATER BUDGET & RESCORING"
)

if not st.session_state.get("analysis_completed"):
    render_empty_analysis_notice()
    if st.button("🚀 GO TO MISSION CONTROL", use_container_width=True):
        st.switch_page("pages/1_mission_control.py")
else:
    farm_name = st.session_state.get("farm_name", "Target Sector")
    coords = st.session_state.get("coords", (33.5779, -101.8552))
    base_climate = st.session_state.get("climate_data", {})
    soil_data = st.session_state.get("soil_data", {})
    past_crops = st.session_state.get("past_crops", ["Maize (Corn)", "Soybean"])
    weights = st.session_state.get("priority_weights", {"water": 4, "soil": 5, "econ": 3, "resilience": 4})
    base_rotations = st.session_state.get("top_rotations", [])
    crop_df = st.session_state.get("crop_df")

    render_html("""<div style="font-family: 'Orbitron', monospace; font-size: 1.15rem; font-weight: 800; color: #19F3FF; letter-spacing: 2px; margin-bottom: 12px; text-transform: uppercase;">⚡ SCENARIO CONTROLS</div>""", sidebar=True)

    selected_preset_name = st.sidebar.selectbox(
        "Sensitivity Preset:",
        list(SCENARIO_PRESETS.keys()),
        index=1,
        key="sc_preset_select"
    )
    preset_vals = SCENARIO_PRESETS[selected_preset_name]
    st.sidebar.caption(f"ℹ️ {preset_vals['description']}")

    st.sidebar.markdown("### // PARAMETRIC ANOMALIES")
    temp_anomaly = st.sidebar.slider(
        "🌡️ Temperature Anomaly (°C):",
        -1.0, 4.0, float(preset_vals["temp_anomaly_c"]), 0.1,
        key="sl_temp_anom"
    )
    rain_change = st.sidebar.slider(
        "🌧️ Precipitation Shift (%):",
        -40.0, 40.0, float(preset_vals["rain_change_pct"]), 5.0,
        key="sl_rain_shift"
    )
    irrigation_alloc = st.sidebar.slider(
        "💧 Irrigation Water Allotment (%):",
        0, 100, int(preset_vals["irrigation_pct"]), 5,
        key="sl_irrig_pct"
    )
    onset_delay = st.sidebar.slider(
        "⏳ Monsoon / Rain Onset Lag (Weeks):",
        0, 6, int(preset_vals["onset_delay_weeks"]), 1,
        key="sl_onset_lag"
    )
    dry_spell_shift = st.sidebar.slider(
        "☀️ Dry Spell Duration Shift (Days):",
        -2.0, 8.0, float(preset_vals["dry_spell_shift"]), 0.5,
        key="sl_dry_shift"
    )

    sc_climate = apply_climate_scenario(
        baseline_climate=base_climate,
        lat=coords[0],
        temp_anomaly_c=temp_anomaly,
        rain_change_pct=rain_change,
        irrigation_pct=irrigation_alloc,
        onset_delay_weeks=onset_delay,
        dry_spell_shift=dry_spell_shift
    )

    st.session_state["active_scenario"] = {
        "name": selected_preset_name,
        "temp_anomaly_c": temp_anomaly,
        "rain_change_pct": rain_change,
        "irrigation_pct": irrigation_alloc,
        "onset_delay_weeks": onset_delay,
        "dry_spell_shift": dry_spell_shift,
        "scenario_climate": sc_climate,
        "disclaimer": "Hypothetical user-defined sensitivity simulation, not an official IPCC projection."
    }

    rescored_rotations = rescore_rotations_under_scenario(
        crop_df=crop_df,
        past_crops=past_crops,
        weights=weights,
        scenario_climate=sc_climate,
        soil_data=soil_data,
        baseline_rotations=base_rotations
    )
    rescored_baseline = evaluate_baseline_monoculture(
        past_crops[1], crop_df, sc_climate, soil_data, weights
    )

    sc_badge = render_provenance_badge("MODELED / SIMULATED", "Sensitivity Test")
    render_html(f"""
    <div class="holo-metric-card" style="margin-bottom: 20px;">
      <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap;">
        <div>
          <div class="holo-label">ACTIVE CLIMATE SIMULATION MATRIX</div>
          <div style="font-family: 'Orbitron', monospace; font-size: 1.35rem; color: #FFFFFF; margin: 4px 0;">{selected_preset_name}</div>
          <div style="font-family: 'Share Tech Mono', monospace; font-size: 0.88rem; color: #FF9E1F;">
            PERTURBATION: {temp_anomaly:+0.1f}°C TEMP • {rain_change:+0.1f}% PRECIP • {irrigation_alloc}% IRRIGATION • {onset_delay} WKS DELAY
          </div>
        </div>
        <div>{sc_badge}</div>
      </div>
      <div style="margin-top: 10px; font-family: 'Rajdhani', sans-serif; font-size: 0.95rem; color: #8FA6B8; border-top: 1px solid rgba(25, 243, 255, 0.15); padding-top: 8px;">
        <em>DISCLAIMER:</em> Hypothetical sensitivity what-if analysis designed for relative resilience screening. <strong>Not an official downscaled climate prediction or crop yield guarantee.</strong>
      </div>
    </div>
    """)

    render_html('<div class="module-header">01 // IMPACT ON AGROCLIMATIC INDICATORS</div>')
    
    col_sc1, col_sc2, col_sc3, col_sc4 = st.columns(4)
    with col_sc1:
        rain_delta = sc_climate["mean_annual_rainfall_mm"] - base_climate["mean_annual_rainfall_mm"]
        render_html(f"""
        <div class="holo-metric-card">
          <div class="holo-label">SCENARIO ANNUAL RAIN</div>
          <div class="holo-val">{sc_climate['mean_annual_rainfall_mm']:.0f} <span style="font-size:0.9rem; color:#8FA6B8;">mm</span></div>
          <div class="holo-delta {'positive' if rain_delta >= 0 else 'amber'}">BASELINE: {base_climate['mean_annual_rainfall_mm']:.0f} mm ({rain_delta:+0.0f} mm)</div>
        </div>
        """)

    with col_sc2:
        temp_delta = sc_climate["mean_annual_temp_c"] - base_climate["mean_annual_temp_c"]
        render_html(f"""
        <div class="holo-metric-card">
          <div class="holo-label">SCENARIO MEAN TEMP</div>
          <div class="holo-val">{sc_climate['mean_annual_temp_c']:.1f} <span style="font-size:0.9rem; color:#8FA6B8;">°C</span></div>
          <div class="holo-delta amber">BASELINE: {base_climate['mean_annual_temp_c']:.1f} °C ({temp_delta:+0.1f} °C)</div>
        </div>
        """)

    with col_sc3:
        hot_delta = sc_climate["hot_days_per_year"] - base_climate["hot_days_per_year"]
        render_html(f"""
        <div class="holo-metric-card">
          <div class="holo-label">EXTREME HEAT DAYS (>35°C)</div>
          <div class="holo-val">{sc_climate['hot_days_per_year']} <span style="font-size:0.9rem; color:#8FA6B8;">DAYS</span></div>
          <div class="holo-delta amber">BASELINE: {base_climate['hot_days_per_year']} DAYS ({hot_delta:+d} DAYS)</div>
        </div>
        """)

    with col_sc4:
        deficit = sc_climate["climatic_water_deficit_mm"]
        render_html(f"""
        <div class="holo-metric-card">
          <div class="holo-label">FAO-56 ET0 WATER BALANCE</div>
          <div class="holo-val" style="color: {'#2CFFB0' if deficit >= 0 else '#FF9E1F'};">{deficit:+0.0f} <span style="font-size:0.9rem; color:#8FA6B8;">mm</span></div>
          <div class="holo-delta {'positive' if deficit >= 0 else 'amber'}">REF ET0: {sc_climate['reference_et0_mm']:.0f} mm/yr</div>
        </div>
        """)

    with st.expander("📖 FAO-56 Hargreaves-Samani Reference Evapotranspiration Formula & Calculation Method"):
        render_html(r"""
        <div style="font-family: 'Share Tech Mono', monospace; font-size: 0.88rem; color: #E8F6FF; line-height: 1.8;">
          <div>$$ET_0 = 0.0023 \times R_a \times (T_{mean} + 17.8) \times \sqrt{T_{max} - T_{min}}$$</div>
          <div style="margin-top: 8px; color: #8FA6B8;">
            • $R_a$: Extraterrestrial solar radiation at top of atmosphere computed from site latitude per FAO Drainage Paper No. 56.<br/>
            • $T_{mean}$: Mean 2-meter air temperature (°C).<br/>
            • $\Delta T = T_{max} - T_{min}$: Diurnal temperature difference reflecting regional humidity and cloudiness.<br/>
            • Climatic Water Deficit: Annual Precipitation Supply minus Reference $ET_0$. Negative values indicate irrigation demand.
          </div>
        </div>
        """)

    render_html('<div class="module-header" style="margin-top: 30px;">02 // RESILIENCE RANKING: BASELINE VS. SCENARIO SHIFT</div>')

    st.markdown(f"**Current Monoculture Baseline ({past_crops[1]}):** Baseline Score: `52.8` ➔ Scenario Score: `{rescored_baseline['composite_score']}`")

    for i, r in enumerate(rescored_rotations[:3]):
        crops = r["crops"]
        seq_str = " ➔ ".join(crops)
        b_rank_str = f"Rank #{r['baseline_rank']}" if r['baseline_rank'] else "Unranked"
        delta_color = "#2CFFB0" if r["score_delta"] >= 0 else "#FF9E1F"
        
        card_class = "rotation-hero-card rank-1" if i == 0 else "rotation-hero-card"
        badge_class = "rank-badge gold" if i == 0 else "rank-badge cyan"

        timeline_html = f"""<div class="crop-timeline"><div class="crop-node">SEASON 1: {crops[0]}</div><div class="crop-arrow">➔</div><div class="crop-node">SEASON 2: {crops[1]}</div><div class="crop-arrow">➔</div><div class="crop-node">SEASON 3: {crops[2]}</div></div>"""
        gauges_html = f"""<div class="gauge-grid">{render_arc_gauge(r['s_water'], 'WATER FIT', '#19F3FF')}{render_arc_gauge(r['s_soil'], 'SOIL HEALTH', '#2CFFB0')}{render_arc_gauge(r['s_resilience'], 'RESILIENCE', '#FF9E1F')}{render_arc_gauge(r['s_econ'], 'MARKET STABILITY', '#80F9FF')}</div>"""

        deficit_notice = f"Unmet Irrigation Deficit: <strong>{r['unmet_water_deficit_mm']} mm/yr</strong>" if r['unmet_water_deficit_mm'] > 0 else "Full Water Requirement Met by Rain + Irrigation"

        render_html(f"""
        <div class="{card_class}">
          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
            <div class="{badge_class}">SCENARIO RANK #{i+1} (SCORE: {r['composite_score']}/100)</div>
            <div style="font-family: 'Share Tech Mono', monospace; font-size: 0.85rem; color: #8FA6B8;">
              BASELINE POSITION: <span style="color: #19F3FF;">{b_rank_str}</span> | SCORE DELTA: <span style="color: {delta_color};">{r['score_delta']:+0.1f} PTS</span>
            </div>
          </div>
          {timeline_html}
          {gauges_html}
          <div style="font-family: 'Share Tech Mono', monospace; font-size: 0.85rem; color: #8FA6B8; margin-top: 8px;">
            <span style="color: #FF9E1F;">WATER STRESS STATUS:</span> {deficit_notice} • <span style="color: #19F3FF;">ANNUAL DEMAND:</span> {r['annual_water_need_mm']} mm/yr
          </div>
          <div style="margin-top: 10px; font-family: 'Rajdhani', sans-serif; font-size: 0.95rem; color: #E8F6FF; line-height: 1.5; border-left: 2px solid #FF9E1F; padding-left: 12px;">
            <strong>SCENARIO ADAPTATION RATIONALE:</strong> {r['rationale']}
          </div>
        </div>
        """)

    render_html('<div class="module-header" style="margin-top: 30px;">03 // SCENARIO COMPARATIVE TRAJECTORIES</div>')

    df_base_series = pd.DataFrame(base_climate["annual_series"])
    df_sc_series = pd.DataFrame(sc_climate["annual_series"])

    col_ch1, col_ch2 = st.columns(2)
    with col_ch1:
        fig_comp_rain = go.Figure()
        fig_comp_rain.add_trace(go.Bar(
            x=df_base_series["year"],
            y=df_base_series["rain"],
            name="Baseline Rainfall (mm)",
            marker=dict(color="#19F3FF", opacity=0.45)
        ))
        fig_comp_rain.add_trace(go.Bar(
            x=df_sc_series["year"],
            y=df_sc_series["rain"],
            name="Scenario Rainfall (mm)",
            marker=dict(color="#FF9E1F", opacity=0.85)
        ))
        apply_vault_plotly_theme(fig_comp_rain, f"RAINFALL DYNAMICS: BASELINE VS. SCENARIO — {farm_name}")
        st.plotly_chart(fig_comp_rain, use_container_width=True)

    with col_ch2:
        fig_comp_temp = go.Figure()
        fig_comp_temp.add_trace(go.Scatter(
            x=df_base_series["year"],
            y=df_base_series["temp"],
            name="Baseline Temp (°C)",
            mode="lines",
            line=dict(color="#8FA6B8", dash="dash", width=2)
        ))
        fig_comp_temp.add_trace(go.Scatter(
            x=df_sc_series["year"],
            y=df_sc_series["temp"],
            name="Scenario Temp (°C)",
            mode="lines+markers",
            line=dict(color="#FF3B3B", width=2.5),
            marker=dict(color="#FF3B3B", size=5)
        ))
        apply_vault_plotly_theme(fig_comp_temp, f"TEMPERATURE ANOMALY TRAJECTORY — {farm_name}")
        st.plotly_chart(fig_comp_temp, use_container_width=True)

    render_html('<div class="module-header" style="margin-top: 30px;">04 // SENSITIVITY UNCERTAINTY DISCLOSURE</div>')
    render_html("""
    <div class="holo-metric-card">
      <div style="font-family: 'Rajdhani', sans-serif; font-size: 1rem; color: #E8F6FF; line-height: 1.8;">
        <div>• <strong>CO₂ Fertilization Effect:</strong> Elevated atmospheric CO₂ can enhance water-use efficiency in C3 plants; this physiological compensation is not explicitly simulated in this sensitivity model.</div>
        <div>• <strong>Extreme Weather Clustering:</strong> Severe rainfall events concentrated into short sub-daily cloudbursts risk runoff losses rather than effective infiltration into the root zone.</div>
        <div>• <strong>Pest & Pathogen Migration:</strong> Warming winter minimum temperatures often fail to freeze overwintering insect pupae, increasing spring pressure.</div>
        <div>• <strong>Economic Market Fluctuations:</strong> Global commodity price swings and local transport tariffs will dictate true net farm income.</div>
      </div>
    </div>
    """)
