"""
FieldShift AI Agronomist (Page 4).
Context-Grounded Agronomic Dialog & Decision Support Powered by Google GenAI (Gemini)
and Deterministic Rule-Based Fallback Explainer.
"""

import os
import json
import streamlit as st
import pandas as pd

from core.ui_theme import (
    render_html, inject_vault_styles, render_command_bar,
    render_provenance_badge, render_empty_analysis_notice
)
from core.agronomy_engine import load_crop_database

inject_vault_styles()

render_command_bar(
    "AI AGRONOMIST // GEMINI INTEL",
    "CONTEXT-GROUNDED AGROECOLOGICAL ADVISORY & RULE-BASED EXPLAINABILITY"
)

def get_gemini_api_key() -> str:
    """Attempts to locate Gemini API key from secrets, environment, or session state."""
    if "GEMINI_API_KEY" in st.session_state and st.session_state["GEMINI_API_KEY"]:
        return st.session_state["GEMINI_API_KEY"]
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    return os.environ.get("GEMINI_API_KEY", "")

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

    rotations_summary = []
    for r in top_rotations[:3]:
        rotations_summary.append({
            "sequence": " -> ".join(r["crops"]),
            "composite_score": r["composite_score"],
            "water_fit_score": r["s_water"],
            "soil_health_score": r["s_soil"],
            "resilience_score": r["s_resilience"],
            "market_stability_score": r["s_econ"],
            "annual_water_demand_mm": r["annual_water_need_mm"],
            "rationale": r["rationale"]
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
            "organic_carbon_g_kg": soil.get("organic_carbon_g_kg", 12.0),
            "total_nitrogen_g_kg": soil.get("total_nitrogen_g_kg", 1.1),
            "phosphorus_mg_kg": soil.get("phosphorus_mg_kg", 18.0),
            "potassium_cmol_kg": soil.get("potassium_cmol_kg", 0.65),
            "is_manual_override": soil.get("source", "").find("Manual") != -1
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
    """
    q_lower = prompt.lower()
    farm = context["location"]["sector_name"]
    rain = context["historical_climate_indicators"]["mean_annual_rainfall_mm"]
    temp = context["historical_climate_indicators"]["mean_annual_temp_c"]
    heat_days = context["historical_climate_indicators"]["extreme_heat_days_gt_35c"]
    texture = context["soil_edaphic_profile"]["texture_class"]
    ph = context["soil_edaphic_profile"]["ph"]
    soc = context["soil_edaphic_profile"]["organic_carbon_g_kg"]
    top_rot = context["recommended_rotations"][0] if context["recommended_rotations"] else None
    top_seq = top_rot["sequence"] if top_rot else "Chickpea -> Sorghum -> Chickpea"
    
    is_simple = (mode == "Simple (Farmer Advisory)")

    if any(k in q_lower for k in ["why", "chickpea", "sorghum", "recommend", "rotation"]):
        if is_simple:
            return (
                f"### 🌱 Why this rotation is recommended for {farm}:\n\n"
                f"1. **Water Conservation:** Your sector receives an average of **{rain:.0f} mm of rainfall per year**. "
                f"The recommended sequence (**{top_seq}**) requires approximately **{top_rot['annual_water_demand_mm']} mm/year**, "
                f"meaning it fits your rainfall budget without draining groundwater reserves.\n"
                f"2. **Natural Nitrogen Fertilizer:** Starting with a legume like Chickpea fixes atmospheric nitrogen into your **{texture}** soil, "
                f"nourishing the following Sorghum crop and reducing synthetic fertilizer costs.\n"
                f"3. **Heat & Drought Tolerance:** Sorghum possesses deep taproots and stay-green physiology, allowing it to withstand the **{heat_days} extreme heat days (>35°C)** recorded in your region.\n"
                f"4. **Disease Break:** Rotating away from continuous monocultures interrupts soil-borne fungal pathogens.\n\n"
                f"*Data Provenance: [NASA POWER Agroclimatology] & [FAO-56 Irrigation Paper]*"
            )
        else:
            return (
                f"### 🔬 Agronomic Rationale & Physiological Analysis — {farm}\n\n"
                f"**1. Soil-Water Mass Balance ($ET_c$ Matching):**\n"
                f"Historical 15-year NASA POWER reanalysis establishes mean annual precipitation at $\\bar{{P}} = {rain:.1f}\\text{{ mm}}$. "
                f"The `{top_seq}` sequence possesses an aggregate seasonal crop evapotranspiration requirement of $\\approx {top_rot['annual_water_demand_mm']}\\text{{ mm}}$, "
                f"yielding a minimal hydrologic deficit compared to high-demand monocultures (e.g., Maize $\\approx 650\\text{{ mm}}$).\n\n"
                f"**2. Edaphic Stratigraphy & Symbiotic Diazotrophy:**\n"
                f"The local soil profile exhibits `{texture}` with baseline $\\text{{pH}} = {ph:.1f}$ and organic carbon at ${soc:.1f}\\text{{ g/kg}}$. "
                f"Inoculation with *Mesorhizobium ciceri* under these edaphic conditions facilitates biological nitrogen fixation (BNF), delivering an estimated $40-65\\text{{ kg N/ha}}$ "
                f"residual nitrogen credit into Horizon A ($0-30\\text{{ cm}}$).\n\n"
                f"**3. Thermal Resilience:**\n"
                f"With ${heat_days}\\text{{ days/yr}}$ exceeding $35^\\circ\\text{{C}}$, Sorghum's $C_4$ photosynthetic pathway and high stomatal control mitigate anthesis sterility.\n\n"
                f"*(Note: Consult local county agricultural extension agents for field-scale cultivar validation.)*"
            )

    elif any(k in q_lower for k in ["heat", "temperature", "warming", "35", "drought", "climate"]):
        return (
            f"### 🌡️ Thermal Stress & Warming Impact Assessment — {farm}\n\n"
            f"- **Warming Velocity:** NASA POWER telemetry records a local warming trend of **+{context['historical_climate_indicators']['warming_rate_c_decade']:.2f}°C per decade**, "
            f"with an average of **{heat_days} days/year exceeding 35°C**.\n"
            f"- **Vulnerability Window:** High temperatures occurring during crop flowering (anthesis) risk pollen desiccation and floret sterility.\n"
            f"- **Mitigation Strategy:** "
            f"1. Shift planting windows to allow anthesis before peak mid-summer thermal spikes.\n"
            f"2. Maintain surface residue (stubble mulching) to depress soil surface temperatures by 3-5°C in topsoil.\n"
            f"3. Select $C_4$ drought-hardy crops (such as Grain Sorghum) or taprooted legumes that access deep moisture reserves in Horizon B ($30-100\\text{{ cm}}$).\n\n"
            f"*Provenance: NASA POWER Daily Agroclimatology Reanalysis (1/2° grid resolution).*"
        )

    elif any(k in q_lower for k in ["soil", "carbon", "cover", "ph", "organic"]):
        return (
            f"### 🧪 Soil Health & Organic Carbon Strategy — {farm}\n\n"
            f"- **Baseline Stratigraphy:** Horizon A topsoil is classified as **{texture}** with **pH {ph:.1f}** and **{soc:.1f} g/kg organic carbon** (ISRIC SoilGrids 250m).\n"
            f"- **Carbon Sequestration:** Incorporating a Cover Crop (Clover-Rye) or Sorghum high-lignin root biomass increases stable humic matter, improving moisture infiltration.\n"
            f"- **Nutrient Management:** The current soil profile shows total N at **{context['soil_edaphic_profile']['total_nitrogen_g_kg']} g/kg** and P at **{context['soil_edaphic_profile']['phosphorus_mg_kg']} mg/kg**. "
            f"A leguminous pre-crop reduces inorganic synthetic urea requirements while preserving mycorrhizal fungal networks.\n\n"
            f"*Recommendation: Conduct a standard 15-core composite soil sampling test per 10 acres to confirm lab-grade fertility metrics.*"
        )

    elif any(k in q_lower for k in ["kannada", "hindi", "language"]):
        return (
            f"### 🌐 Multi-Lingual Agronomic Intelligence\n\n"
            f"**English:** The optimal crop sequence for {farm} is {top_seq}.\n\n"
            f"**Hindi (हिंदी):** {farm} के लिए अनुशंसित फसल चक्र `{top_seq}` है। यह कम पानी ({rain:.0f} मिमी वर्षा) में मिट्टी की सेहत और सूखे से बचाव के लिए सबसे उपयुक्त है।\n\n"
            f"**Kannada (ಕನ್ನಡ):** {farm} ಪ್ರದೇಶಕ್ಕೆ ಶಿಫಾರಸು ಮಾಡಲಾದ ಬೆಳೆ ಸರದಿ `{top_seq}` ಆಗಿದೆ. ಇದು ಕಡಿಮೆ ಮಳೆಯಲ್ಲಿ ({rain:.0f} ಮಿಮೀ) ಮಣ್ಣಿನ ಫಲವತ್ತತೆ ಮತ್ತು ಬರ ನಿರೋಧಕತೆಯನ್ನು ಹೆಚ್ಚಿಸುತ್ತದೆ.\n\n"
            f"*ಗಮನಿಸಿ: ಸ್ಥಳೀಯ ಕೃಷಿ ವಿಜ್ಞಾನ ಕೇಂದ್ರ (KVK) ಜೊತೆ ಸಮಾಲೋಚಿಸಿ.*"
        )

    else:
        return (
            f"### 📋 Strategic Agronomic Brief for {farm}\n\n"
            f"**1. Sector Environment:**\n"
            f"- **Location:** Lat {context['location']['latitude']:.4f}, Lon {context['location']['longitude']:.4f}\n"
            f"- **Rainfall:** {rain:.0f} mm/yr • **Mean Temperature:** {temp:.1f}°C • **Extreme Heat Days:** {heat_days} days/yr\n"
            f"- **Soil Type:** {texture} (pH {ph:.1f}, Soil Organic Carbon: {soc:.1f} g/kg)\n\n"
            f"**2. Optimal Rotation:** **{top_seq}** (Resilience Score: **{top_rot['composite_score']}/100**)\n"
            f"- **Annual Water Requirement:** {top_rot['annual_water_demand_mm']} mm/yr\n"
            f"- **Nitrogen Benefit:** Legume cycle delivers natural N fixation.\n"
            f"- **Thermal Buffer:** Deep rooting breaks plow pans and accesses subsoil moisture.\n\n"
            f"**3. Suggested Next Actions:**\n"
            f"- Verify local soil phosphorus and potassium using the Soil Sampling Planner on Page 5.\n"
            f"- Test climate anomaly sensitivities on Page 2.\n"
            f"- Consult regional extension services for localized seed variety selection.\n\n"
            f"*Generated by FieldShift Rule-Based Agronomic Knowledge Engine.*"
        )

def query_gemini_agronomist(prompt: str, context: dict, api_key: str, mode: str, language: str) -> str:
    """
    Calls the official Google GenAI SDK to generate a grounded, responsible agronomic recommendation.
    """
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)

    is_simple = (mode == "Simple (Farmer Advisory)")
    style_instruction = (
        "Respond in practical, accessible language suitable for a farmer. Keep steps concise and actionable."
        if is_simple else
        "Respond as a Senior Research Agronomist. Provide detailed physiological, edaphic, and biochemical explanations with FAO citations."
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

    model_name = "gemini-2.5-flash"
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.25,
            )
        )
        return response.text
    except Exception as e:
        try:
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.25,
                )
            )
            return response.text
        except Exception as inner_e:
            raise RuntimeError(f"Gemini API Error: {str(inner_e)}")

if not st.session_state.get("analysis_completed"):
    render_empty_analysis_notice()
    if st.button("🚀 GO TO MISSION CONTROL", use_container_width=True):
        st.switch_page("pages/1_mission_control.py")
else:
    farm_name = st.session_state.get("farm_name", "Target Sector")
    farm_context = build_grounded_farm_context(st.session_state)

    if "chat_messages" not in st.session_state:
        st.session_state["chat_messages"] = [
            {
                "role": "assistant",
                "content": f"Greetings Commander. I am your FieldShift AI Agronomist, calibrated for **{farm_name}**. How can I assist with your rotation strategy, soil chemistry, or climate resilience today?"
            }
        ]

    render_html("""<div style="font-family: 'Orbitron', monospace; font-size: 1.15rem; font-weight: 800; color: #19F3FF; letter-spacing: 2px; margin-bottom: 12px; text-transform: uppercase;">⚙️ ADVISOR CONFIG</div>""", sidebar=True)

    detected_key = get_gemini_api_key()
    key_status = "🟢 ACTIVE (Google GenAI)" if detected_key else "🟡 OFFLINE (Rule-Based Fallback)"
    st.sidebar.markdown(f"**Engine Status:** `{key_status}`")

    with st.sidebar.expander("🔑 Gemini API Key Configuration", expanded=(not bool(detected_key))):
        user_key = st.text_input(
            "Enter Gemini API Key:",
            value=st.session_state.get("GEMINI_API_KEY", detected_key),
            type="password",
            help="Get your free key from Google AI Studio (aistudio.google.com/apikey). Keys are not stored on disk."
        )
        if user_key != st.session_state.get("GEMINI_API_KEY", ""):
            st.session_state["GEMINI_API_KEY"] = user_key
            st.rerun()

        st.caption("ℹ️ *If no key is provided, the platform automatically runs our deterministic FAO-56 rule-based agronomic engine.*")

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

    engine_badge_type = "LIVE API" if detected_key else "APPROXIMATE TABLE"
    engine_name = "Google Gemini 2.5 Flash" if detected_key else "Rule-Based Agronomic Engine"
    badge_html = render_provenance_badge(engine_badge_type, engine_name)

    render_html(f"""
    <div class="holo-metric-card" style="margin-bottom: 20px;">
      <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap;">
        <div>
          <div class="holo-label">AGRONOMIC DECISION SUPPORT // {farm_name.upper()}</div>
          <div style="font-family: 'Orbitron', monospace; font-size: 1.35rem; color: #FFFFFF; margin: 4px 0;">
            INTELLIGENT ROTATION & RESILIENCE ADVISOR
          </div>
          <div style="font-family: 'Share Tech Mono', monospace; font-size: 0.88rem; color: #19F3FF;">
            MODE: {selected_mode.upper()} • LANGUAGE: {selected_lang.upper()} • ENGINE: {engine_name.upper()}
          </div>
        </div>
        <div>{badge_html}</div>
      </div>
    </div>
    """)

    st.markdown("#### // QUICK INQUIRY CHIPS")
    col_q1, col_q2, col_q3 = st.columns(3)
    pending_prompt = None

    with col_q1:
        if st.button("🌱 Why is this rotation recommended?", use_container_width=True):
            pending_prompt = "Why is the top rotation recommended for this farm?"
        if st.button("🌡️ How does extreme heat affect this field?", use_container_width=True):
            pending_prompt = "How do the extreme heat days (>35°C) affect crop growth and water demand?"

    with col_q2:
        if st.button("🧪 How can I improve soil organic carbon?", use_container_width=True):
            pending_prompt = "What management practices will increase soil organic carbon in this texture?"
        if st.button("💧 How does rainfall compare to crop water need?", use_container_width=True):
            pending_prompt = "How does our annual rainfall compare with the crop water requirements in this rotation?"

    with col_q3:
        if st.button("🦠 What is the nitrogen credit benefit?", use_container_width=True):
            pending_prompt = "Explain the nitrogen fixation benefit and fertilizer reduction for this sequence."
        if st.button("🌐 Multi-lingual regional summary", use_container_width=True):
            pending_prompt = "Provide a summary in regional languages (Hindi and Kannada) for local farmers."

    render_html('<div class="module-header" style="margin-top: 20px;">02 // TACTICAL AGRONOMIC DIALOG</div>')

    for msg in st.session_state["chat_messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Ask about rotation strategies, soil nutrients, climate risks, or planting dates...")
    effective_prompt = pending_prompt if pending_prompt else user_input

    if effective_prompt:
        st.session_state["chat_messages"].append({"role": "user", "content": effective_prompt})
        with st.chat_message("user"):
            st.markdown(effective_prompt)

        with st.chat_message("assistant"):
            with st.spinner("Synthesizing agroecological telemetry..."):
                current_api_key = get_gemini_api_key()
                if current_api_key:
                    try:
                        ai_response = query_gemini_agronomist(
                            prompt=effective_prompt,
                            context=farm_context,
                            api_key=current_api_key,
                            mode=selected_mode,
                            language=selected_lang
                        )
                    except Exception as err:
                        st.warning(f"⚠️ Live Gemini API connection failed ({str(err)}). Switching to rule-based agronomic explainer.")
                        ai_response = generate_rule_based_response(
                            prompt=effective_prompt,
                            context=farm_context,
                            mode=selected_mode,
                            language=selected_lang
                        )
                else:
                    ai_response = generate_rule_based_response(
                        prompt=effective_prompt,
                        context=farm_context,
                        mode=selected_mode,
                        language=selected_lang
                    )

            st.markdown(ai_response)
            st.session_state["chat_messages"].append({"role": "assistant", "content": ai_response})
            st.rerun()

    with st.expander("🔍 View Grounded Farm Context Payload Sent to AI"):
        st.json(farm_context)
