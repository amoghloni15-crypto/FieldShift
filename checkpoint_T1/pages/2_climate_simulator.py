"""
FieldShift Climate Scenario Simulator (Page 2 - Starter).
"""

import streamlit as st
from core.ui_theme import render_html, inject_vault_styles, render_command_bar, render_empty_analysis_notice

inject_vault_styles()

render_command_bar(
    "CLIMATE SCENARIO SIMULATOR",
    "WHAT-IF SENSITIVITY MODELING • HISTORICAL SERIES STRESS TESTING"
)

if not st.session_state.get("analysis_completed"):
    render_empty_analysis_notice()
    if st.button("🚀 GO TO MISSION CONTROL", use_container_width=True):
        st.switch_page("pages/1_mission_control.py")
else:
    farm_name = st.session_state.get("farm_name", "Active Sector")
    render_html(f"""
    <div class="holo-metric-card">
      <div class="holo-label">SCENARIO TESTING ENGINE ACTIVE</div>
      <div style="font-family: 'Orbitron', monospace; font-size: 1.3rem; color: #19F3FF; margin-top: 4px;">TARGET: {farm_name}</div>
      <div style="font-family: 'Rajdhani', sans-serif; font-size: 1rem; color: #E8F6FF; margin-top: 8px;">
        Module Tier 2 ready for initialization. Test temperature anomalies, precipitation shifts, and irrigation availability against NASA historical series.
      </div>
    </div>
    """)
