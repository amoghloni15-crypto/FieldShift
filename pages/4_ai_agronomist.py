"""
FieldShift AI Agronomist (Page 4).
Context-Grounded Agronomic Dialog & Decision Support Powered by Google GenAI (Gemini)
and Deterministic Rule-Based Fallback Explainer.
"""

import os
import re
import time
import json
import streamlit as st
import pandas as pd

from core.ui_theme import (
    render_html, inject_vault_styles, render_command_bar,
    render_provenance_badge, render_empty_analysis_notice,
    render_error_boundary, fmt_num
)
from core.agronomy_engine import load_crop_database

inject_vault_styles()

render_command_bar(
    "AI AGRONOMIST // GEMINI INTEL",
    "CONTEXT-GROUNDED AGROECOLOGICAL ADVISORY & RULE-BASED EXPLAINABILITY"
)

def sanitize_error_message(err_str: str) -> str:
    """Removes any potential API keys or sensitive auth tokens from error output."""
    clean = re.sub(r'AIza[0-9A-Za-z\-_]{35}', '[REDACTED_API_KEY]', str(err_str))
    clean = re.sub(r'key=[0-9A-Za-z\-_]{20,}', 'key=[REDACTED]', clean)
    clean = re.sub(r'Bearer\s+[0-9A-Za-z\-_]{20,}', 'Bearer [REDACTED]', clean)
    return clean

def get_gemini_api_key() -> tuple[str, str]:
    """
    Attempts to locate Gemini API key from session state, secrets.toml, or environment.
    Returns (api_key, source_name).
    """
    if "GEMINI_API_KEY" in st.session_state and st.session_state["GEMINI_API_KEY"]:
        return st.session_state["GEMINI_API_KEY"].strip(), "Session State Override"
    try:
        if "GEMINI_API_KEY" in st.secrets and st.secrets["GEMINI_API_KEY"]:
            return str(st.secrets["GEMINI_API_KEY"]).strip(), "Streamlit Secrets (.streamlit/secrets.toml)"
    except Exception:
        pass
    env_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if env_key:
        return env_key, "Environment Variable (GEMINI_API_KEY)"
    return "", "None (Offline Fallback)"

def build_grounded_farm_context(session_state) -> dict:
    """Builds a compact, strictly structured JSON payload of the active farm's state."""
    farm_name = session_state.get("farm_name", "Target Sector")
    coords = session_state.get("coords", (33.5779, -101.8552))
    climate = session_state.get("climate_data", {})
    soil = session_state.get("soil_data", {})
    past_crops = session_state.get("past_crops", ["Maize (Corn)", "Soybean"])
    weights = session_state.get("priority_weights", {"water": 4, "soil": 5, "econ": 3, "resilience": 4})
    top_rotations = session_state.get("top_rotations", [])
    active_scenario = session_state.get("active_scenario", None)

    # Simplified rotations for LLM token efficiency
    rotations_summary = []
    for r in top_rotations[:3]:
        rotations_summary.append({
            "sequence": " -> ".join(r.get("crops", [])),
            "composite_score": r.get("composite_score"),
            "water_fit_score": r.get("s_water"),
            "soil_health_score": r.get("s_soil"),
            "resilience_score": r.get("s_resilience"),
            "market_stability_score": r.get("s_econ"),
            "annual_water_demand_mm": r.get("annual_water_need_mm"),
            "rationale": r.get("rationale")
        })

    return {
        "location": {
            "sector_name": farm_name,
            "latitude": coords[0],
            "longitude": coords[1]
        },
        "historical_climate_indicators": {
            "source": "NASA POWER Agroclimatology (15-Yr Reanalysis ~50km)",
            "mean_annual_rainfall_mm": climate.get("mean_annual_rainfall_mm", 450),
            "rainfall_trend_pct_decade": climate.get("rainfall_trend_pct", -5.2),
            "mean_annual_temp_c": climate.get("mean_annual_temp_c", 17.0),
            "warming_rate_c_decade": climate.get("warming_rate_c_decade", 0.35),
            "extreme_heat_days_gt_35c": climate.get("hot_days_per_year", 64),
            "dry_spells_per_year": climate.get("dry_spells_per_year", 2.3)
        },
        "soil_edaphic_profile": {
            "source": "ISRIC SoilGrids 250m Baseline",
            "texture_class": soil.get("texture", "Clay Loam"),
            "ph": soil.get("ph", 6.8),
            "clay_pct": soil.get("clay_pct", 28.0),
            "sand_pct": soil.get("sand_pct", 35.0),
            "soc_pct": soil.get("soc_pct", 1.2),
            "organic_carbon_g_kg": soil.get("organic_carbon_g_kg", 12.0),
            "total_nitrogen_g_kg": soil.get("total_nitrogen_g_kg", 1.1),
            "phosphorus_mg_kg": soil.get("phosphorus_mg_kg", 18.0),
            "potassium_cmol_kg": soil.get("potassium_cmol_kg", 0.65),
            "is_manual_override": "Manual" in str(soil.get("source", ""))
        },
        "management_parameters": {
            "historical_crops": past_crops,
            "farmer_priority_weights": weights
        },
        "recommended_rotations": rotations_summary,
        "active_sensitivity_scenario": {
            "preset": active_scenario.get("name") if active_scenario else "Baseline",
            "temp_anomaly_c": active_scenario.get("temp_anomaly_c", 0.0) if active_scenario else 0.0,
            "rain_change_pct": active_scenario.get("rain_change_pct", 0.0) if active_scenario else 0.0,
            "irrigation_pct": active_scenario.get("irrigation_pct", 100) if active_scenario else 100
        } if active_scenario else "None (Historical Baseline)"
    }

def generate_rule_based_response(prompt: str, context: dict, mode: str, language: str) -> str:
    """
    Deterministic rule-based agronomic explainer engine when offline or no API key is set.
    Differentiates all 6 tactical question chips and handles off-topic queries responsibly.
    """
    q_lower = prompt.lower()
    farm = context["location"]["sector_name"]
    rain = context["historical_climate_indicators"]["mean_annual_rainfall_mm"]
    temp = context["historical_climate_indicators"]["mean_annual_temp_c"]
    heat_days = context["historical_climate_indicators"]["extreme_heat_days_gt_35c"]
    warming = context["historical_climate_indicators"]["warming_rate_c_decade"]
    dry_spells = context["historical_climate_indicators"]["dry_spells_per_year"]
    texture = context["soil_edaphic_profile"]["texture_class"]
    ph = context["soil_edaphic_profile"]["ph"]
    soc = context["soil_edaphic_profile"]["soc_pct"]
    clay = context["soil_edaphic_profile"]["clay_pct"]
    
    top_rot = context["recommended_rotations"][0] if context["recommended_rotations"] else None
    top_seq = top_rot["sequence"] if top_rot else "Chickpea -> Sorghum -> Chickpea"
    top_water = top_rot["annual_water_demand_mm"] if top_rot else 420
    top_score = top_rot["composite_score"] if top_rot else 85
    
    is_simple = (mode == "Simple (Farmer Advisory)")

    # 1. QUESTION: Nitrogen credit / biological fixation
    if any(k in q_lower for k in ["nitrogen", "fertilizer", "rhizob", "credit benefit", "fixation"]):
        if is_simple:
            return (
                f"### 🦠 Biological Nitrogen Fixation & Fertilizer Credit — {farm}\n\n"
                f"1. **Natural Soil Enrichment:** The legume phase in `{top_seq}` forms a symbiotic relationship with beneficial soil bacteria (*Rhizobium* / *Mesorhizobium*), capturing inert nitrogen from the air and converting it into plant-available ammonium.\n"
                f"2. **Fertilizer Cost Savings:** In your **{texture}** soil (pH {ph:.1f}), this biological fixation delivers an estimated **40 to 65 kg of residual nitrogen per hectare** to the succeeding crop.\n"
                f"3. **Practical Application:** When planting the cereal phase (e.g., Sorghum or Wheat), you can safely reduce synthetic base nitrogen fertilizer by **20% to 35%**, cutting input costs without sacrificing vegetative vigor.\n"
                f"4. **Soil Ecology:** Organic nitrogen from crop nodules releases gradually throughout the season, minimizing nitrate leaching into local aquifers.\n\n"
                f"*Data Provenance: [ISRIC SoilGrids Edaphic Profile] & [FAO Drainage Paper 56]*"
            )
        else:
            return (
                f"### 🔬 Edaphic Stratigraphy & Diazotrophic Nitrogen Mass Balance — {farm}\n\n"
                f"**1. Diazotrophic Symbiosis Mechanisms:**\n"
                f"Inoculation of legume cultivars under edaphic conditions characterized by `{texture}` (pH {ph:.1f}, SOC {soc:.2f}%) stimulates root hair infection by *Mesorhizobium ciceri* or *Sinorhizobium*, forming indeterminate root nodules in Horizon A (0–30 cm).\n\n"
                f"**2. Quantified N Credit Dynamics:**\n"
                f"- **Gross Fixation (N_fix):** Approximately 60–90 kg N/ha/season depending on canopy leaf area index (LAI).\n"
                f"- **Net Carryover Credit (N_credit):** An estimated **40–65 kg N/ha** remains available for the subsequent non-legume phase after seed harvest.\n"
                f"- **Synthetic Urea Abatement:** Translates to an immediate reduction of approximately 90–140 kg/ha of commercial synthetic urea (46-0-0), lowering direct input expenditures.\n\n"
                f"**3. Environmental Co-Benefits:**\n"
                f"Gradual biological mineralization limits the formation of mobile nitrates (NO3-), mitigating groundwater leaching during recharge events and reducing nitrous oxide (N2O) emissions.\n\n"
                f"*(Note: Verify localized nodulation efficiency with county agricultural extension services.)*"
            )

    # 2. QUESTION: Rainfall vs Crop Water Need
    elif any(k in q_lower for k in ["rainfall compare", "water need", "water demand", "water requirement", "crop water", "et0", "deficit"]):
        water_delta = rain - top_water
        balance_status = "surplus buffer" if water_delta >= 0 else "seasonal deficit"
        return (
            f"### 💧 Hydrological Mass Balance: Rainfall vs. Crop Evapotranspiration — {farm}\n\n"
            f"- **Annual Precipitation:** NASA POWER 15-year reanalysis records mean annual rainfall of **{rain:.0f} mm/year** for this sector.\n"
            f"- **Rotation Water Requirement ($ET_c$):** The top recommended sequence (**{top_seq}**) requires an aggregate **{top_water:.0f} mm/year**.\n"
            f"- **Hydrologic Balance:** **{water_delta:+.0f} mm/year** ({balance_status}).\n\n"
            f"**Agronomic Assessment:**\n"
            f"1. **Monoculture Comparison:** High-water crops (such as continuous Maize at ~650 mm/yr) exceed your natural rainfall envelope, forcing unsustainable groundwater pumping.\n"
            f"2. **Drought Buffering:** The `{top_seq}` sequence uses deep-rooted cereals and drought-tolerant legumes that synchronize peak moisture demand with regional rainfall distributions.\n"
            f"3. **Infiltration & Soil Texture:** In your **{texture}** soil (Clay: {clay:.1f}%), moisture retention is moderate-to-high, allowing effective storage of off-season winter rains in Horizon B.\n\n"
            f"*Data Provenance: [NASA POWER Agroclimatology (2010-2024)] & [FAO-56 Dual Crop Coefficient]*"
        )

    # 3. QUESTION: Heat & Climate Volatility
    elif any(k in q_lower for k in ["heat", "temperature", "warming", "35", "thermal", "drought"]):
        return (
            f"### 🌡️ Thermal Stress & Warming Impact Assessment — {farm}\n\n"
            f"- **Warming Velocity:** NASA POWER telemetry records a local warming trend of **+{warming:.2f}°C per decade**, with an average of **{heat_days} days/year exceeding 35°C**.\n"
            f"- **Dry Spell Frequency:** Long dry spells (>14 consecutive days without rain) occur **{dry_spells:.1f} times per year**.\n"
            f"- **Vulnerability Window:** High temperatures during anthesis (flowering) risk pollen desiccation, aborted seeds, and floret sterility in cool-season crops.\n\n"
            f"**Actionable Mitigation Strategy:**\n"
            f"1. **Physiological Match:** The recommended rotation includes $C_4$ cereals (like Grain Sorghum) exhibiting stay-green genetics and high photosynthetic efficiency up to 38°C.\n"
            f"2. **Planting Date Shift:** Stagger sowing dates by 10-14 days to ensure flowering occurs before the peak July/August thermal window.\n"
            f"3. **Stubble Mulch Retention:** Retaining minimum 30% residue cover on the surface depresses peak soil surface temperature by 3°C to 5°C.\n\n"
            f"*Data Provenance: [NASA POWER Daily Reanalysis (0.5° Grid)]*"
        )

    # 4. QUESTION: Soil Organic Carbon & Soil Health
    elif any(k in q_lower for k in ["soil", "carbon", "soc", "organic", "humus", "ph"]):
        return (
            f"### 🧪 Soil Health & Organic Carbon Strategy — {farm}\n\n"
            f"- **Baseline Edaphic Profile:** Horizon A ($0-30\\text{{ cm}}$) is classified as **{texture}** with **pH {ph:.1f}**, **{soc:.2f}% Soil Organic Carbon (SOC)**, and **{clay:.1f}% clay content** (ISRIC SoilGrids 250m).\n"
            f"- **Carbon Sequestration Roadmap:**\n"
            f"  1. **High-Biomass Roots:** Integrating fibrous-rooted cereals (Sorghum/Rye) deposits recalcitrant root lignin deep into the subsoil profile.\n"
            f"  2. **Reduced / Conservation Tillage:** Strip-till or no-till practices prevent microbial oxidation of existing humus, protecting soil aggregates.\n"
            f"  3. **Cover Cropping:** Maintaining green cover between main seasons stimulates rhizosphere microbial exudates, increasing microbial biomass carbon (MBC).\n"
            f"- **Target Benchmark:** Increasing SOC from {soc:.2f}% to 1.8% will increase field water holding capacity by approximately **18,000 to 22,000 liters per hectare** in the top 30 cm.\n\n"
            f"*Data Provenance: [ISRIC SoilGrids 250m Rest API] & [FAO Soils Portal]*"
        )

    # 5. QUESTION: Multi-lingual summary (Hindi / Kannada)
    elif any(k in q_lower for k in ["hindi", "kannada", "regional", "multi-lingual", "multilingual", "language"]):
        return (
            f"### 🌐 Multi-Lingual Agronomic Intelligence // बहुभाषी कृषि सलाह // ಬಹುಭಾಷಾ ಕೃಷಿ ಸಲಹೆ\n\n"
            f"**English:** The optimal tactical rotation for sector {farm} is `{top_seq}` (Composite Score: {top_score}/100), requiring {top_water:.0f} mm/yr against {rain:.0f} mm annual rainfall.\n\n"
            f"**Hindi (हिंदी):**\n"
            f"- **अनुशंसित फसल चक्र:** `{top_seq}`\n"
            f"- **कारण:** आपके क्षेत्र में औसत वार्षिक वर्षा **{rain:.0f} मिमी** है और अत्यधिक गर्मी ({heat_days} दिन >35°C) पड़ती है। यह चक्र दलहन के माध्यम से मिट्टी में प्राकृतिक नाइट्रोजन जोड़ता है और कम पानी में अधिक उपज व सूखा प्रतिरोधक क्षमता प्रदान करता है।\n"
            f"- **सुझाव:** बुवाई से पहले नजदीकी कृषि विज्ञान केंद्र (KVK) से बीज किस्मों की पुष्टि करें।\n\n"
            f"**Kannada (ಕನ್ನಡ):**\n"
            f"- **ಶಿಫಾರಸು ಮಾಡಿದ ಬೆಳೆ ಸರದಿ:** `{top_seq}`\n"
            f"- **ಪ್ರಯೋಜನ:** ನಿಮ್ಮ ಕ್ಷೇತ್ರದ ಸರಾಸರಿ ಮಳೆ **{rain:.0f} ಮಿಮೀ** ಮತ್ತು ತಾಪಮಾನ {heat_days} ದಿನಗಳು 35°C ಗಿಂತ ಹೆಚ್ಚಿರುತ್ತದೆ. ಈ ಬೆಳೆ ಪದ್ಧತಿಯು ಮಣ್ಣಿನಲ್ಲಿ ಸಾರಜನಕ ಸ್ಥಿರೀಕರಣವನ್ನು ಹೆಚ್ಚಿಸುತ್ತದೆ ಮತ್ತು ತೇವಾಂಶ ಕೊರತೆಯನ್ನು ಸಮರ್ಥವಾಗಿ ನಿಭಾಯಿಸುತ್ತದೆ.\n"
            f"- **ಸಲಹೆ:** ಬಿತ್ತನೆಗೆ ಮುನ್ನ ಸ್ಥಳೀಯ ಕೃಷಿ ವಿಜ್ಞಾನ ಕೇಂದ್ರ (KVK) ಜೊತೆ ಸಮಾಲೋಚಿಸಿ.\n\n"
            f"*Data Provenance: NASA POWER Reanalysis & FieldShift Multi-Lingual Engine.*"
        )

    # 6. QUESTION: Why is this rotation recommended?
    elif any(k in q_lower for k in ["why", "recommend", "rotation", "optimal", "sequence"]):
        if is_simple:
            return (
                f"### 🌱 Why this rotation is recommended for {farm}:\n\n"
                f"1. **Water Conservation:** Your sector receives an average of **{rain:.0f} mm of rainfall per year**. "
                f"The recommended sequence (**{top_seq}**) requires approximately **{top_water:.0f} mm/year**, "
                f"meaning it fits within your natural precipitation budget without over-drafting groundwater.\n"
                f"2. **Natural Nitrogen Fertilizer:** Starting with a legume fixes atmospheric nitrogen into your **{texture}** soil (pH {ph:.1f}), "
                f"nourishing the following crop and reducing synthetic fertilizer costs.\n"
                f"3. **Heat & Drought Tolerance:** The sequence uses crops with deep taproots and heat-tolerant stay-green traits, designed to withstand the **{heat_days} extreme heat days (>35°C)** recorded in your region.\n"
                f"4. **Disease Break:** Rotating away from continuous monocultures interrupts soil-borne fungal spore lifecycles and nematode build-ups.\n\n"
                f"*Data Provenance: [NASA POWER Agroclimatology] & [FAO-56 Irrigation Paper]*"
            )
        else:
            return (
                f"### 🔬 Agronomic Rationale & Physiological Analysis — {farm}\n\n"
                f"**1. Soil-Water Mass Balance (ET_c Matching):**\n"
                f"Historical 15-year NASA POWER reanalysis establishes mean annual precipitation at P = {rain:.1f} mm. "
                f"The `{top_seq}` sequence possesses an aggregate seasonal crop evapotranspiration requirement of ~{top_water:.0f} mm, "
                f"yielding a minimal hydrologic deficit compared to high-demand monocultures (e.g., Maize ~650 mm).\n\n"
                f"**2. Edaphic Stratigraphy & Symbiotic Diazotrophy:**\n"
                f"The local soil profile exhibits `{texture}` with baseline pH = {ph:.1f} and organic carbon at {soc:.2f}%. "
                f"Inoculation with *Mesorhizobium* under these edaphic conditions facilitates biological nitrogen fixation (BNF), delivering an estimated 40–65 kg N/ha "
                f"residual nitrogen credit into Horizon A (0–30 cm).\n\n"
                f"**3. Thermal Resilience:**\n"
                f"With {heat_days} days/year exceeding 35°C, C4 photosynthetic pathways and high stomatal control mitigate anthesis sterility.\n\n"
                f"*(Note: Consult local county agricultural extension agents for field-scale cultivar validation.)*"
            )

    # 7. OFF-TOPIC OR UNRECOGNIZED QUERY (Polite, clear boundary notice)
    else:
        return (
            f"### ⚠️ Offline Agronomic Knowledge Engine Notice\n\n"
            f"The **AI model is currently offline** (no active Google Gemini API key configured). In offline mode, FieldShift operates a deterministic rule-based engine strictly focused on the farm's telemetry.\n\n"
            f"**Your Query:** *\"{prompt}\"*\n\n"
            f"This query falls outside the pre-computed rule set for sector **{farm}**. You can:\n"
            f"1. **Click any of the 6 tactical inquiry chips above** (Rotation Rationale, Extreme Heat, Soil Organic Carbon, Water Budget, Nitrogen Credit, Multi-Lingual Summary).\n"
            f"2. **Connect a Gemini API Key** in the left sidebar to enable live, conversational multi-turn dialog on any general, agronomic, or custom topic."
        )

def query_gemini_agronomist(prompt: str, context: dict, conversation_history: list, api_key: str, mode: str, language: str) -> tuple[str, str]:
    """
    Calls the official Google GenAI SDK to generate a grounded agronomic recommendation.
    Supports multi-turn context, retries with backoff, and model fallback.
    Returns (response_text, model_used).
    """
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)

    is_simple = (mode == "Simple (Farmer Advisory)")
    style_instruction = (
        "Respond in practical, accessible language suitable for an active farmer. Keep steps concise, encouraging, and actionable."
        if is_simple else
        "Respond as a Senior Research Agronomist. Provide detailed physiological, edaphic, and biochemical explanations with citations to FAO-56, ISRIC, and NASA data."
    )

    lang_instruction = f"Output your entire answer strictly in the language: {language}." if language != "English" else ""

    system_instruction = f"""
You are the FieldShift Planetary AI Agronomist, a specialized decision-support agent for the NASA Space Apps Challenge 2026.
You provide precise, evidence-based agricultural advice grounded strictly in the provided JSON farm context.

GROUNDED FARM CONTEXT JSON:
{json.dumps(context, indent=2)}

STRICT OPERATIONAL RULES:
1. Grounding: Answer the user's inquiry strictly utilizing the provided farm context (location, NASA POWER climate reanalysis, SoilGrids profile, rotation scores).
2. DO NOT Hallucinate: NEVER invent specific crop yields (e.g. do not say "You will harvest 4.5 tons/acre"), and NEVER guarantee financial profits or revenues.
3. Provenance Transparency: Clearly cite data provenance tags in brackets (e.g. [NASA POWER 15-Yr Reanalysis], [ISRIC SoilGrids], [FAO-56 Methodology], [Modeled Sensitivity Scenario]).
4. Climate Reality: Remind the user that NASA POWER data is coarse grid reanalysis (~50 km) and soil values are regional estimates; encourage physical soil testing and local extension validation.
5. Tone & Style: {style_instruction}
6. Language: {lang_instruction}
"""

    # Format multi-turn conversation history for Google GenAI SDK
    contents = []
    # Include up to the last 6 turns to keep context rich yet token-efficient
    recent_history = conversation_history[-6:] if len(conversation_history) > 6 else conversation_history
    for msg in recent_history:
        role = "user" if msg.get("role") == "user" else "model"
        # Skip initial welcome greeting from history
        if "Greetings Commander" in msg.get("content", ""):
            continue
        contents.append(types.Content(role=role, parts=[types.Part.from_text(text=msg.get("content", ""))]))
    
    # Append the current prompt as user turn
    contents.append(types.Content(role="user", parts=[types.Part.from_text(text=prompt)]))

    candidate_models = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
    last_error = None

    for model_name in candidate_models:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.25,
                    )
                )
                if response and response.text:
                    return response.text, model_name
            except Exception as e:
                last_error = e
                # Wait briefly before second attempt or next model
                time.sleep(1.0)

    raise RuntimeError(f"All candidate Gemini models failed: {sanitize_error_message(str(last_error))}")

# MAIN PAGE LOGIC
if not st.session_state.get("analysis_completed"):
    render_empty_analysis_notice()
    if st.button("🚀 GO TO MISSION CONTROL", use_container_width=True):
        st.switch_page("pages/1_mission_control.py")
else:
    try:
        farm_name = st.session_state.get("farm_name", "Target Sector")
        farm_context = build_grounded_farm_context(st.session_state)

        # Initialize chat state
        if "chat_messages" not in st.session_state:
            st.session_state["chat_messages"] = [
                {
                    "role": "assistant",
                    "content": f"Greetings Commander. I am your FieldShift AI Agronomist, calibrated for **{farm_name}**. How can I assist with your rotation strategy, soil chemistry, or climate resilience today?"
                }
            ]

        # Initialize last AI status tracking
        if "last_ai_status" not in st.session_state:
            key, source = get_gemini_api_key()
            if key:
                st.session_state["last_ai_status"] = {
                    "mode": "READY",
                    "model": "gemini-2.0-flash",
                    "source": source,
                    "error": None
                }
            else:
                st.session_state["last_ai_status"] = {
                    "mode": "OFFLINE",
                    "model": "Deterministic Agro-Engine",
                    "source": source,
                    "error": None
                }

        # SIDEBAR: CONFIG & API KEY
        render_html("""<div style="font-family: 'Orbitron', monospace; font-size: 1.15rem; font-weight: 800; color: #19F3FF; letter-spacing: 2px; margin-bottom: 12px; text-transform: uppercase;">⚙️ ADVISOR CONFIG</div>""", sidebar=True)

        detected_key, key_source = get_gemini_api_key()
        has_key = bool(detected_key)

        with st.sidebar.expander("🔑 Gemini API Key Configuration", expanded=(not has_key)):
            st.markdown(
                """
                **How to configure a Gemini API key:**
                1. Obtain a key from [Google AI Studio](https://aistudio.google.com/apikey).
                2. Enter it below for this session, or set `GEMINI_API_KEY` in `.streamlit/secrets.toml`.
                3. The key stays local to your browser session and is never logged or exposed.
                """
            )
            user_key_input = st.text_input(
                "Gemini API Key:",
                value=st.session_state.get("GEMINI_API_KEY", ""),
                type="password",
                help="Enter key to enable live conversational reasoning."
            )
            if user_key_input != st.session_state.get("GEMINI_API_KEY", ""):
                st.session_state["GEMINI_API_KEY"] = user_key_input.strip()
                st.rerun()

            st.caption(f"**Key Source:** `{key_source}`")

        selected_mode = st.sidebar.radio(
            "Advisory Mode:",
            ["Simple (Farmer Advisory)", "Technical (Agronomic Research)"],
            index=0,
            key="advisor_mode_radio"
        )

        selected_lang = st.sidebar.selectbox(
            "Response Language:",
            ["English", "Hindi (हिंदी)", "Kannada (ಕನ್ನಡ)", "Spanish (Español)"],
            index=0,
            key="advisor_lang_select"
        )

        if st.sidebar.button("🧹 Clear Chat History", use_container_width=True):
            st.session_state["chat_messages"] = [
                {
                    "role": "assistant",
                    "content": f"Telemetry reset. AI Agronomist standing by for **{farm_name}**."
                }
            ]
            st.rerun()

        # HUD STATUS BADGE
        last_status = st.session_state.get("last_ai_status", {})
        status_mode = last_status.get("mode", "OFFLINE")
        active_model = last_status.get("model", "Deterministic Agro-Engine")

        if status_mode == "LIVE":
            hud_badge_color = "#2CFFB0"
            hud_badge_bg = "rgba(44, 255, 176, 0.12)"
            hud_badge_border = "#2CFFB0"
            hud_badge_text = f"🟢 AI MODEL: LIVE ({active_model})"
        elif status_mode == "ERROR":
            hud_badge_color = "#FF9E1F"
            hud_badge_bg = "rgba(255, 158, 31, 0.14)"
            hud_badge_border = "#FF9E1F"
            hud_badge_text = f"🟡 AI MODEL: OFFLINE FALLBACK — CONNECTION FAULT"
        else:
            hud_badge_color = "#19F3FF"
            hud_badge_bg = "rgba(25, 243, 255, 0.10)"
            hud_badge_border = "#19F3FF"
            hud_badge_text = f"🟡 AI MODEL: OFFLINE FALLBACK (Deterministic Agro-Engine)"

        render_html(f"""
        <div class="holo-metric-card" style="margin-bottom: 20px;">
          <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px;">
            <div>
              <div class="holo-label">AGRONOMIC DECISION SUPPORT // {farm_name.upper()}</div>
              <div style="font-family: 'Orbitron', monospace; font-size: 1.3rem; color: #FFFFFF; margin: 4px 0;">
                INTELLIGENT ROTATION & RESILIENCE ADVISOR
              </div>
              <div style="font-family: 'Share Tech Mono', monospace; font-size: 0.88rem; color: #19F3FF;">
                MODE: {selected_mode.upper()} • LANGUAGE: {selected_lang.upper()} • SOURCE: {key_source.upper()}
              </div>
            </div>
            <div>
              <div style="background: {hud_badge_bg}; border: 1px solid {hud_badge_border}; border-radius: 6px; padding: 6px 14px; font-family: 'Share Tech Mono', monospace; font-size: 0.85rem; font-weight: 700; color: {hud_badge_color}; letter-spacing: 1px;">
                {hud_badge_text}
              </div>
            </div>
          </div>
        </div>
        """)

        # If there is a recorded diagnostic fault, show it in an expander
        if last_status.get("error"):
            with st.expander("🔍 AI Diagnostics & Fallback Reason", expanded=False):
                st.warning(f"Live Gemini API was not reached: {last_status['error']}. FieldShift automatically engaged the verified deterministic rule-based engine.")

        # QUICK QUESTION CHIPS
        st.markdown("#### // TACTICAL INQUIRY CHIPS")
        col_q1, col_q2, col_q3 = st.columns(3)

        with col_q1:
            if st.button("🌱 Why is this rotation recommended?", use_container_width=True):
                st.session_state["pending_prompt"] = "Why is the top rotation recommended for this farm?"
                st.rerun()
            if st.button("🌡️ How does extreme heat affect this field?", use_container_width=True):
                st.session_state["pending_prompt"] = "How do the extreme heat days (>35°C) affect crop growth and water demand?"
                st.rerun()

        with col_q2:
            if st.button("🧪 How can I improve soil organic carbon?", use_container_width=True):
                st.session_state["pending_prompt"] = "What management practices will increase soil organic carbon in this texture?"
                st.rerun()
            if st.button("💧 How does rainfall compare to crop water need?", use_container_width=True):
                st.session_state["pending_prompt"] = "How does our annual rainfall compare with the crop water requirements in this rotation?"
                st.rerun()

        with col_q3:
            if st.button("🦠 What is the nitrogen credit benefit?", use_container_width=True):
                st.session_state["pending_prompt"] = "Explain the nitrogen fixation benefit and fertilizer reduction for this sequence."
                st.rerun()
            if st.button("🌐 Multi-lingual regional summary", use_container_width=True):
                st.session_state["pending_prompt"] = "Provide a summary in regional languages (Hindi and Kannada) for local farmers."
                st.rerun()

        # DISPLAY CHAT HISTORY
        render_html('<div class="module-header" style="margin-top: 20px;">02 // TACTICAL AGRONOMIC DIALOG</div>')

        for msg in st.session_state["chat_messages"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # USER CHAT INPUT
        user_input = st.chat_input("Ask about rotation strategies, soil nutrients, climate risks, or planting dates...")
        effective_prompt = st.session_state.pop("pending_prompt", None) or user_input

        if effective_prompt:
            st.session_state["chat_messages"].append({"role": "user", "content": effective_prompt})
            with st.chat_message("user"):
                st.markdown(effective_prompt)

            with st.chat_message("assistant"):
                with st.spinner("Synthesizing agroecological telemetry..."):
                    current_api_key, _ = get_gemini_api_key()
                    ai_response = None
                    used_model = None

                    if current_api_key:
                        try:
                            ai_response, used_model = query_gemini_agronomist(
                                prompt=effective_prompt,
                                context=farm_context,
                                conversation_history=st.session_state["chat_messages"][:-1],
                                api_key=current_api_key,
                                mode=selected_mode,
                                language=selected_lang
                            )
                            st.session_state["last_ai_status"] = {
                                "mode": "LIVE",
                                "model": used_model,
                                "source": key_source,
                                "error": None
                            }
                        except Exception as err:
                            clean_err = sanitize_error_message(str(err))
                            st.session_state["last_ai_status"] = {
                                "mode": "ERROR",
                                "model": "Fallback Deterministic Engine",
                                "source": key_source,
                                "error": clean_err
                            }
                            ai_response = generate_rule_based_response(
                                prompt=effective_prompt,
                                context=farm_context,
                                mode=selected_mode,
                                language=selected_lang
                            )
                    else:
                        st.session_state["last_ai_status"] = {
                            "mode": "OFFLINE",
                            "model": "Deterministic Agro-Engine",
                            "source": key_source,
                            "error": None
                        }
                        ai_response = generate_rule_based_response(
                            prompt=effective_prompt,
                            context=farm_context,
                            mode=selected_mode,
                            language=selected_lang
                        )

                st.markdown(ai_response)
                st.session_state["chat_messages"].append({"role": "assistant", "content": ai_response})
                st.rerun()

        # COLLAPSIBLE GROUNDED CONTEXT INSPECTOR
        with st.expander("🔍 View Grounded Farm Context Payload Sent to AI"):
            st.json(farm_context)

    except Exception as e:
        render_error_boundary("AI Agronomist Subsystem", e)
