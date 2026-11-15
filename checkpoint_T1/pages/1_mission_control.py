"""
FieldShift Tactical Mission Control (Page 1).
Hero 3D Earth Cockpit, Command Panel, 15-Yr Climate Intel, Top Rotation Recommendations & Sensor Map.
"""

import os
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go

from core.presets import PRESETS, check_is_farmland
from core.climate_service import fetch_nasa_power_data
from core.soil_service import fetch_soilgrids_data
from core.gibs_service import get_verified_gibs_tile_url
from core.agronomy_engine import load_crop_database, generate_and_score_rotations, evaluate_baseline_monoculture
from core.ui_theme import (
    render_html, inject_vault_styles, render_command_bar,
    apply_vault_plotly_theme, render_arc_gauge, render_provenance_badge
)

# Inject shared styling
inject_vault_styles()

# Load Crop Database
crop_df = load_crop_database()

# Import Bidirectional Globe Component (declared in core module)
from core.globe_component import globe_component

# Initialize Session State Variables
if "location_mode_radio" not in st.session_state:
    st.session_state["location_mode_radio"] = "Benchmark Farm"
if "custom_lat_input" not in st.session_state:
    st.session_state["custom_lat_input"] = 33.5779
if "custom_lon_input" not in st.session_state:
    st.session_state["custom_lon_input"] = -101.8552
if "last_locked_id" not in st.session_state:
    st.session_state["last_locked_id"] = None
if "prev_lat" not in st.session_state:
    st.session_state.prev_lat = 33.5779
    st.session_state.prev_lon = -101.8552
    st.session_state.is_first_load = True
else:
    st.session_state.is_first_load = False

# Check if target lock was received from the 3D globe component
globe_val = st.session_state.get("globe_selector")
if isinstance(globe_val, dict) and globe_val.get("id"):
    if globe_val.get("id") != st.session_state.get("last_locked_id"):
        st.session_state["last_locked_id"] = globe_val["id"]
        st.session_state["location_mode_radio"] = "Custom Coordinates"
        st.session_state["custom_lat_input"] = float(globe_val["lat"])
        st.session_state["custom_lon_input"] = float(globe_val["lon"])
        st.toast(f"🎯 Target Locked: {globe_val['lat']:+.4f}°, {globe_val['lon']:+.4f}°", icon="🛰️")

# SIDEBAR: THE COMMAND PANEL
render_html("""<div style="font-family: 'Orbitron', monospace; font-size: 1.15rem; font-weight: 800; color: #19F3FF; letter-spacing: 2px; margin-bottom: 12px; text-transform: uppercase;">⚡ COMMAND PANEL</div>""", sidebar=True)

st.sidebar.markdown("### // 01 SECTOR SELECT")
location_mode = st.sidebar.radio(
    "Coordinate Source:",
    ["Benchmark Farm", "Custom Coordinates"],
    key="location_mode_radio"
)

if location_mode == "Benchmark Farm":
    selected_preset = st.sidebar.selectbox("Benchmark Sector:", list(PRESETS.keys()), index=0, key="preset_select")
    farm_info = PRESETS[selected_preset]
    latitude = float(farm_info["lat"])
    longitude = float(farm_info["lon"])
    location_display_name = selected_preset
    climate_classification = farm_info.get("climate_type", "Continental Agro-zone")
else:
    selected_preset = None
    latitude = float(st.sidebar.number_input(
        "Latitude (°N/S):",
        min_value=-60.0,
        max_value=75.0,
        step=0.01,
        key="custom_lat_input"
    ))
    longitude = float(st.sidebar.number_input(
        "Longitude (°E/W):",
        min_value=-180.0,
        max_value=180.0,
        step=0.01,
        key="custom_lon_input"
    ))
    location_display_name = f"Custom Field ({latitude:+.4f}°, {longitude:+.4f}°)"
    climate_classification = "Custom Arable Sector"

st.sidebar.markdown("### // 02 CROPPING LOG")
available_crops = crop_df["crop_name"].tolist()
default_past1 = farm_info["default_past_crops"][0] if selected_preset else available_crops[0]
default_past2 = farm_info["default_past_crops"][1] if selected_preset else available_crops[1]

past_crop_2 = st.sidebar.selectbox("Season -2 Crop:", available_crops, index=available_crops.index(default_past1) if default_past1 in available_crops else 0, key="past_c2")
past_crop_1 = st.sidebar.selectbox("Season -1 Crop:", available_crops, index=available_crops.index(default_past2) if default_past2 in available_crops else 1, key="past_c1")

st.sidebar.markdown("### // 03 TACTICAL PRIORITIES")
w_water = st.sidebar.slider("💧 Water Conservation", 1, 5, 4, key="sl_water")
w_soil = st.sidebar.slider("🪵 Soil Health & Organic Carbon", 1, 5, 5, key="sl_soil")
w_econ = st.sidebar.slider("📈 Market / Income Stability", 1, 5, 3, key="sl_econ")
w_resilience = st.sidebar.slider("☀️ Thermal & Drought Resilience", 1, 5, 4, key="sl_resil")

st.sidebar.markdown("### // 04 SOIL TEST OVERRIDE")
use_custom_soil = st.sidebar.checkbox("Manual Soil Lab Override", value=False, key="chk_override")

override_clay = st.sidebar.number_input("Clay Content (%)", 0.0, 100.0, 24.0, key="num_clay") if use_custom_soil else 24.0
override_sand = st.sidebar.number_input("Sand Content (%)", 0.0, 100.0, 52.0, key="num_sand") if use_custom_soil else 52.0
override_soc = st.sidebar.number_input("Organic Carbon (%)", 0.0, 20.0, 1.2, key="num_soc") if use_custom_soil else 1.2
override_ph = st.sidebar.number_input("Soil pH", 3.5, 9.5, 7.2, key="num_ph") if use_custom_soil else 7.2

# Fetch NASA Climate & ISRIC Soil Data
live_climate = fetch_nasa_power_data(latitude, longitude)
live_soil = fetch_soilgrids_data(latitude, longitude)

if selected_preset in PRESETS:
    p_info = PRESETS[selected_preset]
    climate_data = live_climate if live_climate else {
        **p_info["fallback_climate"],
        "source": "NASA POWER Verified Archive (Local Cache)",
        "provenance": "FALLBACK DEMO DATA"
    }
    base_soil_data = live_soil if live_soil else {
        **p_info["fallback_soil"],
        "source": "ISRIC SoilGrids Verified Archive (Local Cache)",
        "provenance": "FALLBACK DEMO DATA"
    }
else:
    if abs(latitude) < 23.5:
        ref = PRESETS["Nakuru, Rift Valley, Kenya (Equatorial Highland)"]
    elif abs(latitude) > 45.0:
        ref = PRESETS["Poltava, Ukraine (Eurasian Chernozem Steppe)"]
    elif longitude > 60:
        ref = PRESETS["Ludhiana, Punjab, India (Indo-Gangetic Plain)"]
    elif latitude < 0:
        ref = PRESETS["Dubbo, New South Wales, Australia (Murray-Darling)"]
    elif longitude < -98:
        ref = PRESETS["Lubbock, Texas, USA (Semi-Arid High Plains)"]
    else:
        ref = PRESETS["Ames, Iowa, USA (Humid Corn Belt)"]

    climate_data = live_climate if live_climate else {
        **ref["fallback_climate"],
        "source": "NASA POWER Regional Reference Baseline",
        "provenance": "FALLBACK DEMO DATA"
    }
    base_soil_data = live_soil if live_soil else {
        **ref["fallback_soil"],
        "source": "ISRIC SoilGrids Regional Baseline",
        "provenance": "FALLBACK DEMO DATA"
    }

# Validate Farmland vs Ocean/Ice
is_farmland = check_is_farmland(latitude, longitude, base_soil_data)

btn_analyze = st.sidebar.button(
    "⚡ INITIALIZE TACTICAL ANALYSIS",
    use_container_width=True,
    disabled=not is_farmland
)

user_weights = {
    "water": float(w_water),
    "soil": float(w_soil),
    "econ": float(w_econ),
    "resilience": float(w_resilience)
}

if use_custom_soil:
    active_soil_data = {
        "clay_pct": override_clay,
        "sand_pct": override_sand,
        "soc_pct": override_soc,
        "ph": override_ph,
        "source": "Farmer Lab Test (Manual Override)",
        "provenance": "FARMER INPUT"
    }
else:
    active_soil_data = base_soil_data

# Real Status Indicators
is_nasa_live = "Live" in climate_data.get("source", "")
nasa_chip_class = "chip-active" if is_nasa_live else "chip-fallback"
nasa_chip_text = "🟢 NASA POWER: LIVE API" if is_nasa_live else "🟡 NASA ARCHIVE (CACHED)"

# TOP COMMAND BAR
command_bar_html = f"""<div class="command-bar"><div><div class="command-title">MISSION CONTROL // FIELDSHIFT</div><div class="command-subtitle">EARTH OBSERVATION DECISION INTELLIGENCE • NASA SPACE APPS 2026</div></div><div class="status-chip-container"><div class="status-chip {nasa_chip_class}">{nasa_chip_text}</div><div class="status-chip chip-target">📍 TARGET: {latitude:+.2f}°, {longitude:+.2f}°</div></div></div>"""
render_html(command_bar_html)

# HERO 3D COCKPIT VIEWPORT (BIDIRECTIONAL GLOBE)
globe_component(
    target_lat=latitude,
    target_lon=longitude,
    target_label=location_display_name,
    is_first_load=st.session_state.is_first_load,
    key="globe_selector"
)

st.session_state.prev_lat = latitude
st.session_state.prev_lon = longitude

# NON-FARMLAND / OCEAN SAFEGUARD BANNER
if not is_farmland:
    ocean_warning_html = f"""<div style="background: rgba(255, 59, 59, 0.15); border: 1px solid #FF3B3B; border-radius: 8px; padding: 16px 20px; margin: 18px 0; font-family: 'Share Tech Mono', monospace; color: #FF3B3B; box-shadow: 0 0 24px rgba(255,59,59,0.25);"><div style="font-family: 'Orbitron', monospace; font-size: 1.05rem; font-weight: 800; letter-spacing: 1.5px; display: flex; align-items: center; gap: 8px;"><span>⚠️ SENSOR WARNING</span> // NO FARMLAND DATA AT THIS POINT</div><div style="font-size: 0.9rem; margin-top: 6px; color: #E8F6FF; line-height: 1.5;">The crosshair reticle is currently positioned over open water, polar ice, or non-arable maritime coordinates ({latitude:+.4f}°, {longitude:+.4f}°). Rotate the 3D globe to a continental agricultural region, align the reticle, and click <strong>LOCK TARGET</strong> to calibrate analysis.</div></div>"""
    render_html(ocean_warning_html)

# MODULE 01: CLIMATE INTEL & SOIL PROFILE
soil_badge = render_provenance_badge(active_soil_data.get("provenance", "LIVE API"), "0-30cm Depth")
climate_badge = render_provenance_badge(climate_data.get("provenance", "LIVE API"), "NASA POWER 2010-2024")

render_html(f"""<div class="module-header"><span style="flex-grow:1;">01 // CLIMATE & SOIL INTEL — {location_display_name.upper()}</span><div style="display:flex; gap:8px;">{climate_badge}{soil_badge}</div></div>""")

col_m1, col_m2, col_m3, col_m4 = st.columns(4)
with col_m1:
    m1_html = f"""<div class="holo-metric-card"><div class="holo-label">ANNUAL PRECIPITATION</div><div class="holo-val">{climate_data['mean_annual_rainfall_mm']} <span style="font-size:0.9rem; color:#8FA6B8;">mm</span></div><div class="holo-delta {'positive' if climate_data['rainfall_trend_pct'] >= 0 else 'amber'}">DECADE TREND: {climate_data['rainfall_trend_pct']:+.1f}%</div></div>"""
    render_html(m1_html)

with col_m2:
    m2_html = f"""<div class="holo-metric-card"><div class="holo-label">MEAN TEMPERATURE</div><div class="holo-val">{climate_data['mean_annual_temp_c']} <span style="font-size:0.9rem; color:#8FA6B8;">°C</span></div><div class="holo-delta amber">WARMING: +{climate_data['warming_rate_c_decade']:.2f} °C / DECADE</div></div>"""
    render_html(m2_html)

with col_m3:
    m3_html = f"""<div class="holo-metric-card"><div class="holo-label">EXTREME HEAT EXPOSURE</div><div class="holo-val">{climate_data['hot_days_per_year']} <span style="font-size:0.9rem; color:#8FA6B8;">DAYS/YR</span></div><div class="holo-delta amber">THRESHOLD: >35°C PEAK TEMP</div></div>"""
    render_html(m3_html)

with col_m4:
    soc_display = f"{active_soil_data['soc_pct']:.2f}" if is_farmland else "N/A"
    texture_display = f"{active_soil_data['clay_pct']}% CLAY | pH {active_soil_data['ph']}" if is_farmland else "OPEN WATER"
    m4_html = f"""<div class="holo-metric-card"><div class="holo-label">SOIL ORGANIC CARBON (SOC)</div><div class="holo-val">{soc_display} <span style="font-size:0.9rem; color:#8FA6B8;">%</span></div><div class="holo-delta {'positive' if is_farmland else 'amber'}">TEXTURE: {texture_display}</div></div>"""
    render_html(m4_html)

# MODULE 02: ROTATION STRATEGY BENCHMARKING
model_badge = render_provenance_badge("MODELED / SIMULATED", "FAO Rule Engine")
render_html(f"""<div class="module-header"><span style="flex-grow:1;">02 // TACTICAL ROTATION STRATEGIES (RANKED VS. STATUS QUO) — {location_display_name.upper()}</span>{model_badge}</div>""")

if not is_farmland:
    st.info("Cropping rotation optimization paused: Target coordinates are over non-arable terrain. Select a terrestrial farm location to generate crop sequence models.")
    top_rotations = []
    baseline = {}
else:
    top_rotations = generate_and_score_rotations(
        crop_df,
        [past_crop_2, past_crop_1],
        user_weights,
        climate_data,
        active_soil_data
    )
    baseline = evaluate_baseline_monoculture(past_crop_1, crop_df, climate_data, active_soil_data, user_weights)

    # PERSIST EVERYTHING IN SESSION STATE FOR ALL SUBPAGES
    st.session_state["analysis_completed"] = True
    st.session_state["farm_name"] = location_display_name
    st.session_state["coords"] = (latitude, longitude)
    st.session_state["climate_type"] = climate_classification
    st.session_state["climate_data"] = climate_data
    st.session_state["soil_data"] = active_soil_data
    st.session_state["past_crops"] = [past_crop_2, past_crop_1]
    st.session_state["priority_weights"] = user_weights
    st.session_state["top_rotations"] = top_rotations
    st.session_state["baseline_monoculture"] = baseline
    st.session_state["crop_df"] = crop_df
    st.session_state["is_farmland"] = is_farmland

    if not top_rotations:
        st.warning("No rotation sequence satisfied current constraints. Adjust field cropping parameters.")
    else:
        for idx, r in enumerate(top_rotations[:3]):
            is_top = (idx == 0)
            card_class = "rotation-hero-card rank-1" if is_top else "rotation-hero-card"
            badge_class = "rank-badge gold" if is_top else "rank-badge cyan"
            badge_text = f"★ RANK #{idx+1} OPTIMAL STRATEGY (COMPOSITE {r['composite_score']}/100)" if is_top else f"RANK #{idx+1} ALTERNATIVE ({r['composite_score']}/100)"
            
            crops = r["crops"]
            timeline_html = f"""<div class="crop-timeline"><div class="crop-node">SEASON 1: {crops[0]}</div><div class="crop-arrow">➔</div><div class="crop-node">SEASON 2: {crops[1]}</div><div class="crop-arrow">➔</div><div class="crop-node">SEASON 3: {crops[2]}</div></div>"""
            
            gauges_html = f"""<div class="gauge-grid">{render_arc_gauge(r['s_water'], 'WATER FIT', '#19F3FF')}{render_arc_gauge(r['s_soil'], 'SOIL HEALTH', '#2CFFB0')}{render_arc_gauge(r['s_resilience'], 'RESILIENCE', '#FF9E1F')}{render_arc_gauge(r['s_econ'], 'MARKET STABILITY', '#80F9FF')}</div>"""
            
            water_saved = baseline["annual_water_need_mm"] - r["annual_water_need_mm"]
            diff_text = f"Conserves {water_saved} mm water/yr vs. continuous {baseline['crop_name']}" if water_saved > 0 else f"Water demand +{-water_saved} mm/yr"
            
            card_html = f"""<div class="{card_class}"><div class="{badge_class}">{badge_text}</div>{timeline_html}{gauges_html}<div style="font-family: 'Share Tech Mono', monospace; font-size: 0.85rem; color: #8FA6B8; margin-top: 8px;"><span style="color: #2CFFB0;">HYDROL-IMPACT:</span> {diff_text} • <span style="color: #19F3FF;">BIODIVERSITY:</span> {r['legume_seasons']} Legume Season(s) • {len(r['families'])} Families</div><div style="margin-top: 10px; font-family: 'Rajdhani', sans-serif; font-size: 0.95rem; color: #E8F6FF; line-height: 1.5; border-left: 2px solid #19F3FF; padding-left: 12px;"><strong>AGRONOMIC RATIONALE:</strong> {r['rationale']}</div></div>"""
            render_html(card_html)

# MODULE 03: INTERACTIVE CHARTS & DIAGNOSTICS
render_html(f'<div class="module-header">03 // ADVANCED DIAGNOSTICS & COMPARATIVE GRAPHS — {location_display_name.upper()}</div>')

tab1, tab2, tab3, tab4 = st.tabs([
    "📈 15-YR CLIMATE INTEL",
    "💧 WATER BUDGET MATRIX",
    "🗺️ SENSOR MAP & SOIL",
    "📚 FAO SOURCES & DATA"
])

with tab1:
    df_climate_series = pd.DataFrame(climate_data["annual_series"])
    col_c1, col_c2 = st.columns(2)
    
    with col_c1:
        fig_rain = go.Figure()
        fig_rain.add_trace(go.Bar(
            x=df_climate_series["year"],
            y=df_climate_series["rain"],
            name="Precipitation (mm)",
            marker=dict(color="#19F3FF", opacity=0.85)
        ))
        fig_rain.add_hline(
            y=climate_data["mean_annual_rainfall_mm"],
            line_dash="dash",
            line_color="#2CFFB0",
            annotation_text=f"15-yr Normal: {climate_data['mean_annual_rainfall_mm']} mm",
            annotation_font=dict(color="#2CFFB0", family="Share Tech Mono")
        )
        apply_vault_plotly_theme(fig_rain, f"ANNUAL RAINFALL VS. 15-YR NORMAL — {location_display_name}")
        st.plotly_chart(fig_rain, use_container_width=True)

    with col_c2:
        fig_temp = go.Figure()
        fig_temp.add_trace(go.Scatter(
            x=df_climate_series["year"],
            y=df_climate_series["temp"],
            name="Mean Temp (°C)",
            mode="lines+markers",
            line=dict(color="#FFFFFF", width=2.5),
            marker=dict(color="#19F3FF", size=6)
        ))
        fig_temp.add_trace(go.Bar(
            x=df_climate_series["year"],
            y=df_climate_series["hot_days"],
            name="Hot Days (>35°C)",
            marker=dict(color="#FF9E1F", opacity=0.65),
            yaxis="y2"
        ))
        fig_temp.update_layout(
            yaxis2=dict(
                title=dict(text="Hot Days Count", font=dict(color="#FF9E1F")),
                overlaying="y",
                side="right",
                showgrid=False,
                tickfont=dict(family="Share Tech Mono", color="#FF9E1F")
            )
        )
        apply_vault_plotly_theme(fig_temp, f"TEMPERATURE & EXTREME HEAT TREND — {location_display_name}")
        st.plotly_chart(fig_temp, use_container_width=True)

with tab2:
    if is_farmland and 'top_rotations' in locals() and top_rotations:
        comp_labels = ["Current Practice"] + [f"Rank #{i+1}" for i in range(min(3, len(top_rotations)))]
        water_values = [baseline["annual_water_need_mm"]] + [r["annual_water_need_mm"] for r in top_rotations[:3]]

        col_w1, col_w2 = st.columns(2)
        with col_w1:
            fig_water = go.Figure()
            fig_water.add_trace(go.Bar(
                x=comp_labels,
                y=water_values,
                name="Annual Water Need (mm)",
                marker=dict(color=["#FF3B3B", "#2CFFB0", "#19F3FF", "#80F9FF"], opacity=0.85)
            ))
            fig_water.add_hline(
                y=climate_data["mean_annual_rainfall_mm"],
                line_dash="dot",
                line_color="#19F3FF",
                line_width=2,
                annotation_text=f"NASA Rain: {climate_data['mean_annual_rainfall_mm']} mm",
                annotation_font=dict(color="#19F3FF", family="Share Tech Mono")
            )
            apply_vault_plotly_theme(fig_water, f"WATER DEMAND VS. NASA RAIN ENVELOPE — {location_display_name}")
            st.plotly_chart(fig_water, use_container_width=True)

        with col_w2:
            categories = ["Water Fit", "Soil Health", "Climate Resilience", "Market Stability"]
            fig_radar = go.Figure()
            
            fig_radar.add_trace(go.Scatterpolar(
                r=[baseline["s_water"], baseline["s_soil"], baseline["s_resilience"], baseline["s_econ"]],
                theta=categories,
                fill="toself",
                name="Current Practice",
                line=dict(color="#FF3B3B", width=2),
                fillcolor="rgba(255, 59, 59, 0.15)"
            ))
            
            r1 = top_rotations[0]
            fig_radar.add_trace(go.Scatterpolar(
                r=[r1["s_water"], r1["s_soil"], r1["s_resilience"], r1["s_econ"]],
                theta=categories,
                fill="toself",
                name="Rank #1 Strategy",
                line=dict(color="#19F3FF", width=2.5),
                fillcolor="rgba(25, 243, 255, 0.22)"
            ))

            fig_radar.update_layout(
                polar=dict(
                    bgcolor="rgba(10, 17, 24, 0.8)",
                    radialaxis=dict(visible=True, range=[0, 100], gridcolor="rgba(25, 243, 255, 0.15)", tickfont=dict(family="Share Tech Mono", color="#8FA6B8")),
                    angularaxis=dict(gridcolor="rgba(25, 243, 255, 0.15)", tickfont=dict(family="Rajdhani", color="#E8F6FF", size=12))
                ),
                showlegend=True
            )
            apply_vault_plotly_theme(fig_radar, f"AGRONOMIC RESILIENCE MATRIX — {location_display_name}")
            st.plotly_chart(fig_radar, use_container_width=True)
    else:
        st.info("Water budget matrix and agronomic radar require arable terrestrial coordinates.")

with tab3:
    col_map1, col_map2 = st.columns([0.65, 0.35])
    
    with col_map1:
        tile_url, layer_label, layer_date, max_zoom = get_verified_gibs_tile_url(latitude, longitude)
        
        map_header_html = f"""<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;"><span style="font-family: 'Orbitron', monospace; font-size: 0.8rem; font-weight: 700; color: #19F3FF; letter-spacing: 1px;">// SATELLITE RECON — {layer_label.upper()}</span><span class="status-chip chip-active" style="font-size: 0.68rem; padding: 2px 8px;">🛰️ GIBS: {layer_date}</span></div>"""
        render_html(map_header_html)
        
        fig_map = go.Figure(go.Scattermapbox(
            lat=[latitude],
            lon=[longitude],
            mode='markers+text',
            marker=dict(size=18, color='#FF9E1F' if not is_farmland else '#19F3FF', opacity=0.9),
            text=[f"  {location_display_name}"],
            textposition="top right",
            textfont=dict(family="Share Tech Mono", size=12, color="#19F3FF")
        ))
        fig_map.update_layout(
            mapbox=dict(
                style="white-bg",
                layers=[
                    dict(
                        sourcetype="raster",
                        source=[tile_url],
                        below="traces",
                        minzoom=0,
                        maxzoom=max_zoom
                    )
                ],
                center=dict(lat=latitude, lon=longitude),
                zoom=4.5
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="#0A1118",
            margin=dict(l=0, r=0, t=0, b=0),
            height=360,
            annotations=[
                dict(
                    text="Imagery: NASA GIBS / ESDIS (Worldview)",
                    xref="paper",
                    yref="paper",
                    x=0.99,
                    y=0.02,
                    xanchor="right",
                    yanchor="bottom",
                    showarrow=False,
                    font=dict(family="Share Tech Mono", size=10, color="#8FA6B8"),
                    bgcolor="rgba(10, 17, 24, 0.8)",
                    bordercolor="rgba(25, 243, 255, 0.3)",
                    borderwidth=1
                )
            ]
        )
        st.plotly_chart(fig_map, use_container_width=True)

    with col_map2:
        soil_profile_html = f"""<div class="holo-metric-card" style="height: 360px;"><div class="holo-label">SOIL PROFILE (ISRIC SOILGRIDS 0–30 CM)</div><div style="margin-top: 10px; font-family: 'Share Tech Mono', monospace; font-size: 0.95rem; line-height: 1.8;"><div>CLAY FRACTION: <span style="color:#19F3FF;">{active_soil_data['clay_pct']}%</span></div><div>SAND FRACTION: <span style="color:#19F3FF;">{active_soil_data['sand_pct']}%</span></div><div>ORGANIC CARBON: <span style="color:#2CFFB0;">{active_soil_data['soc_pct']}%</span></div><div>SOIL pH (H2O): <span style="color:#FF9E1F;">{active_soil_data['ph']}</span></div></div><div style="margin-top: 14px; font-size: 0.85rem; color: #8FA6B8; line-height: 1.4;"><em>AGRONOMIC INTEL:</em> Soil texture regulates water-holding capacity and root aeration. Diverse crop root profiles buffer seasonal precipitation volatility.</div></div>"""
        render_html(soil_profile_html)

with tab4:
    render_html('<div class="module-header">04 // SCIENTIFIC METHODOLOGY & REFERENCES</div>')
    st.dataframe(crop_df, use_container_width=True, hide_index=True)
    sources_html = """<div style="font-family: 'Rajdhani', sans-serif; font-size: 0.95rem; color: #8FA6B8; line-height: 1.6; margin-top: 12px;"><p><strong style="color: #19F3FF;">1. NASA POWER Project:</strong> Daily agroclimatology dataset (T2M, T2M_MAX, PRECTOTCORR). NASA Langley Research Center. API: <code>https://power.larc.nasa.gov/api/temporal/daily/point</code>.</p><p><strong style="color: #19F3FF;">2. ISRIC SoilGrids 250m v2.0:</strong> Global gridded soil information system. API: <code>https://rest.isric.org/soilgrids/v2.0/properties/query</code>.</p><p><strong style="color: #19F3FF;">3. FAO Irrigation & Drainage Papers No. 56 & 33:</strong> Guidelines for crop water requirements and yield response to water deficits. Food and Agriculture Organization of the United Nations.</p><p><strong style="color: #19F3FF;">4. Planetary Textures:</strong> NASA Blue Marble and Earth at Night imagery compiled by the NASA Earth Observatory, served via three-globe.</p><p><strong style="color: #19F3FF;">5. NASA GIBS / ESDIS:</strong> True-color satellite imagery served via WMTS REST (visual basemap only, no API key required).</p></div>"""
    render_html(sources_html)

# Footer
st.markdown("---")
footer_html = """<div style="text-align: center; font-family: 'Share Tech Mono', monospace; font-size: 0.8rem; color: #546B7E; letter-spacing: 1px;">FIELDSHIFT TACTICAL ROTATION ADVISOR • NASA SPACE APPS CHALLENGE 2026 • OPEN SCIENCE DECISION SUPPORT</div>"""
render_html(footer_html)
