"""
FieldShift Tactical Platform (Root Coordinator).
NASA Space Apps Challenge 2026 — "Field Shift: Adapting Farms with NASA Data"
Multi-Page Platform Coordinator with Shared HUD Navigation.
"""

import streamlit as st

# Global Application Configuration
st.set_page_config(
    page_title="FieldShift Tactical Command | NASA Space Apps 2026",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Multi-Page Navigation Architecture
pg = st.navigation({
    "TACTICAL PLATFORM": [
        st.Page("pages/1_mission_control.py", title="MISSION CONTROL", icon="🛰️", default=True),
        st.Page("pages/2_climate_simulator.py", title="CLIMATE SIMULATOR", icon="⚡"),
        st.Page("pages/3_digital_twin.py", title="DIGITAL TWIN", icon="🌱"),
        st.Page("pages/4_ai_agronomist.py", title="AI AGRONOMIST", icon="🤖"),
    ],
    "ANALYSIS & GOVERNANCE": [
        st.Page("pages/5_farm_report.py", title="FARM REPORT & EXPORTS", icon="📋"),
        st.Page("pages/6_methodology_data.py", title="METHODOLOGY & DATA", icon="📚"),
    ]
})

pg.run()
