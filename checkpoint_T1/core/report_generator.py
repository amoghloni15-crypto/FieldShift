"""
FieldShift Tactical Farm Report & Multi-Format Export Generator.
Generates:
1. Executive PDF Farm Dossier via ReportLab (with embedded Matplotlib climate figures)
2. Machine-readable JSON Export
3. Tabular CSV Dataset
"""

import io
import os
import json
import pandas as pd
from datetime import datetime, timezone

# Ensure Matplotlib uses D: drive temp directory
os.environ["MPLCONFIGDIR"] = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "temp_mpl")
os.makedirs(os.environ["MPLCONFIGDIR"], exist_ok=True)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_climate_chart_image(annual_series: list) -> io.BytesIO:
    """
    Renders 15-year rainfall and temperature trends using Matplotlib.
    """
    df = pd.DataFrame(annual_series)
    fig, ax1 = plt.subplots(figsize=(6.5, 2.4), dpi=180)
    fig.patch.set_facecolor('#070D14')
    ax1.set_facecolor('#0A1118')

    # Rainfall bars
    years = df['year'].values
    rain = df['rain'].values
    ax1.bar(years, rain, color='#19F3FF', alpha=0.6, width=0.6, label='Rainfall (mm)')
    ax1.set_ylabel('Annual Rain (mm)', color='#19F3FF', fontsize=9, fontfamily='sans-serif')
    ax1.tick_params(axis='y', labelcolor='#19F3FF', labelsize=8)
    ax1.tick_params(axis='x', labelcolor='#8FA6B8', labelsize=8)
    ax1.grid(color='#19F3FF', alpha=0.1, linestyle='--')

    # Temperature line
    ax2 = ax1.twinx()
    temp = df['temp'].values
    ax2.plot(years, temp, color='#FF9E1F', marker='o', linewidth=1.5, markersize=3, label='Mean Temp (C)')
    ax2.set_ylabel('Mean Temp (C)', color='#FF9E1F', fontsize=9, fontfamily='sans-serif')
    ax2.tick_params(axis='y', labelcolor='#FF9E1F', labelsize=8)

    ax1.set_title("15-Year Historical Agroclimatology (NASA POWER: 2010-2024)", color='#E8F6FF', fontsize=10, pad=10)

    for spine in ax1.spines.values():
        spine.set_color('#19F3FF')
        spine.set_alpha(0.3)
    for spine in ax2.spines.values():
        spine.set_color('#FF9E1F')
        spine.set_alpha(0.3)

    plt.tight_layout()
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png', facecolor=fig.get_facecolor(), edgecolor='none')
    img_buf.seek(0)
    plt.close(fig)
    return img_buf

def generate_pdf_report(
    farm_name: str,
    coords: tuple,
    climate_type: str,
    climate_data: dict,
    soil_data: dict,
    past_crops: list,
    weights: dict,
    rotations: list,
    baseline_monoculture: dict,
    active_scenario: dict = None
) -> bytes:
    """
    Builds a professional multi-page ReportLab PDF dossier.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom Palette Styles
    c_navy = colors.HexColor("#070D14")
    c_cyan = colors.HexColor("#19F3FF")
    c_amber = colors.HexColor("#FF9E1F")
    c_light = colors.HexColor("#E8F6FF")
    c_muted = colors.HexColor("#8FA6B8")
    c_border = colors.HexColor("#19F3FF")

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0B3D91"),
        spaceAfter=4
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#0A1118"),
        spaceBefore=10,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#222222")
    )

    bullet_style = ParagraphStyle(
        'BulletDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#333333"),
        leftIndent=12
    )

    story = []

    # Title & Metadata Header
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    story.append(Paragraph("FIELDSHIFT TACTICAL ROTATION DOSSIER", title_style))
    story.append(Paragraph(f"<b>NASA Space Apps Challenge 2026</b> | Generated: {now_str}", body_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0B3D91"), spaceBefore=4, spaceAfter=10))

    # Location & Provenance Summary Table
    meta_data = [
        [Paragraph("<b>Target Farm Sector:</b>", body_style), Paragraph(f"{farm_name}", body_style)],
        [Paragraph("<b>Coordinates:</b>", body_style), Paragraph(f"Lat: {coords[0]:.4f}, Lon: {coords[1]:.4f}", body_style)],
        [Paragraph("<b>Agro-Ecological Classification:</b>", body_style), Paragraph(f"{climate_type}", body_style)],
        [Paragraph("<b>Cropping History (Seasons -2, -1):</b>", body_style), Paragraph(f"{past_crops[0]} ➔ {past_crops[1]}", body_style)],
        [Paragraph("<b>Primary Tactical Goal Weights:</b>", body_style), Paragraph(f"Water: {weights.get('water', 3)}/5 | Soil: {weights.get('soil', 3)}/5 | Market: {weights.get('econ', 3)}/5 | Resilience: {weights.get('resilience', 3)}/5", body_style)]
    ]
    t_meta = Table(meta_data, colWidths=[180, 360])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F4F8FA")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#D0E0E8")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 10))

    # Soil Profile & Provenance Table
    story.append(Paragraph("1. SOIL INTELLIGENCE & GROUND PROFILE (ISRIC SOILGRIDS 0-30 CM)", h2_style))
    soil_prov = soil_data.get("provenance", "LIVE API")
    soil_source = soil_data.get("source", "ISRIC SoilGrids 250m v2.0")
    soil_table_data = [
        [Paragraph("<b>Parameter</b>", body_style), Paragraph("<b>Value</b>", body_style), Paragraph("<b>Agronomic Interpretation</b>", body_style), Paragraph("<b>Data Provenance</b>", body_style)],
        [Paragraph("Clay Fraction", body_style), Paragraph(f"{soil_data.get('clay_pct', 'N/A')}%", body_style), Paragraph("Regulates plant-available water holding capacity", body_style), Paragraph(f"{soil_prov}", body_style)],
        [Paragraph("Sand Fraction", body_style), Paragraph(f"{soil_data.get('sand_pct', 'N/A')}%", body_style), Paragraph("Influences percolation rate and drainage permeability", body_style), Paragraph(f"{soil_prov}", body_style)],
        [Paragraph("Soil Organic Carbon (SOC)", body_style), Paragraph(f"{soil_data.get('soc_pct', 'N/A')}%", body_style), Paragraph("Baseline biological soil fertility and structure", body_style), Paragraph(f"{soil_prov}", body_style)],
        [Paragraph("Soil pH (H2O)", body_style), Paragraph(f"{soil_data.get('ph', 'N/A')}", body_style), Paragraph("Controls nutrient availability and root acid/alkaline stress", body_style), Paragraph(f"{soil_prov}", body_style)]
    ]
    t_soil = Table(soil_table_data, colWidths=[110, 60, 250, 120])
    t_soil.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0B3D91")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CCCCCC")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_soil)
    story.append(Spacer(1, 10))

    # Climate Chart & Indicators
    story.append(Paragraph("2. 15-YEAR HISTORICAL CLIMATE VOLATILITY (NASA POWER 2010-2024)", h2_style))
    story.append(Paragraph(
        f"<b>Mean Annual Rain:</b> {climate_data.get('mean_annual_rainfall_mm')} mm | "
        f"<b>10-Yr Rainfall Trend:</b> {climate_data.get('rainfall_trend_pct')}% | "
        f"<b>Warming Rate:</b> +{climate_data.get('warming_rate_c_decade')} C/decade | "
        f"<b>Hot Days (>35C):</b> {climate_data.get('hot_days_per_year')}/yr | "
        f"<b>Dry Spells (>14d):</b> {climate_data.get('dry_spells_per_year')}/yr",
        body_style
    ))
    story.append(Spacer(1, 4))
    
    if "annual_series" in climate_data:
        chart_img = generate_climate_chart_image(climate_data["annual_series"])
        story.append(Image(chart_img, width=540, height=200))
        story.append(Spacer(1, 8))

    # Rotation Recommendations
    story.append(Paragraph("3. STRATEGIC ROTATION ALTERNATIVES VS. CONTINUOUS PRACTICE", h2_style))
    story.append(Paragraph(
        f"<b>Current Monoculture Baseline ({baseline_monoculture.get('crop_name')}):</b> "
        f"Composite Score: {baseline_monoculture.get('composite_score')}/100 "
        f"(Water: {baseline_monoculture.get('s_water')}, Soil: {baseline_monoculture.get('s_soil')}, Resilience: {baseline_monoculture.get('s_resilience')})<br/>"
        f"<i>Vulnerability Note:</i> {baseline_monoculture.get('vulnerability_notes')}",
        body_style
    ))
    story.append(Spacer(1, 6))

    rot_headers = [
        Paragraph("<b>Rank</b>", body_style),
        Paragraph("<b>3-Season Sequence</b>", body_style),
        Paragraph("<b>Score</b>", body_style),
        Paragraph("<b>Water / Soil / Resil</b>", body_style),
        Paragraph("<b>Agronomic Rationale</b>", body_style)
    ]
    rot_rows = [rot_headers]
    for i, r in enumerate(rotations[:3]):
        seq_str = " ➔ ".join(r["crops"])
        scores_str = f"W:{int(r['s_water'])} | S:{int(r['s_soil'])} | R:{int(r['s_resilience'])}"
        rot_rows.append([
            Paragraph(f"<b>#{i+1}</b>", body_style),
            Paragraph(f"<b>{seq_str}</b>", body_style),
            Paragraph(f"<b>{r['composite_score']}</b>", body_style),
            Paragraph(scores_str, body_style),
            Paragraph(r['rationale'], body_style)
        ])

    t_rot = Table(rot_rows, colWidths=[40, 160, 50, 100, 190])
    t_rot.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0A1118")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#B0C4DE")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_rot)
    story.append(Spacer(1, 10))

    # Scenario Simulation Section (if active)
    if active_scenario:
        story.append(Paragraph("4. ACTIVE CLIMATE SCENARIO SENSITIVITY TEST", h2_style))
        story.append(Paragraph(
            f"<b>Scenario Name:</b> {active_scenario.get('name', 'Custom What-If')} | "
            f"<b>Temp Anomaly:</b> {active_scenario.get('temp_anomaly_c', 0):+d} C | "
            f"<b>Rainfall Change:</b> {active_scenario.get('rain_change_pct', 0):+d}% | "
            f"<b>Irrigation Availability:</b> {active_scenario.get('irrigation_pct', 100)}%",
            body_style
        ))
        story.append(Paragraph(f"<i>Disclaimer:</i> {active_scenario.get('disclaimer', 'Hypothetical sensitivity analysis, not an official climate forecast.')}", body_style))
        story.append(Spacer(1, 6))

    # Soil Sampling Planner & Ground Validation Checklist
    story.append(Paragraph("5. COMPREHENSIVE ON-FARM SOIL SAMPLING PLANNER", h2_style))
    story.append(Paragraph("<b>Satellite and gridded proxies CANNOT replace direct soil core testing.</b> The following critical chemical and physical measurements are absent from satellite data and must be verified with certified soil test laboratories:", body_style))
    story.append(Spacer(1, 3))
    
    missing_items = [
        "<b>Available Nitrogen (NO3-N & NH4-N):</b> Satellite sensors cannot penetrate root zones to measure dynamic plant-available nitrogen pools.",
        "<b>Available Phosphorus (Bray-1 / Mehlich-3):</b> Critical for early root proliferation and legume nodulation efficiency.",
        "<b>Exchangeable Potassium (K) & Micronutrients (Zn, Fe, B):</b> Regulate stomatal conductance and high-temperature stress tolerance.",
        "<b>Bulk Density & Hardpan Compaction Depth:</b> Requires mechanical penetrometer or core samples to verify root penetration limits.",
        "<b>Salinity & Electrical Conductivity (ECe):</b> Determines osmotic water uptake constraints under elevated evaporation.",
        "<b>Groundwater Table & Active Infiltration Rate:</b> Local hydrological metrics necessary before converting to high-demand irrigation."
    ]
    for item in missing_items:
        story.append(Paragraph(f"• {item}", bullet_style))
        
    story.append(Spacer(1, 8))

    # Scientific Limitations & Ground Verification Notice
    story.append(Paragraph("6. DECISION SUPPORT LIMITATIONS & SCIENTIFIC SOURCES", h2_style))
    limitations = [
        "<b>Coarse Resolution Notice:</b> NASA POWER climate data is provided at 0.5 x 0.5 degree (~50 km) resolution; ISRIC SoilGrids is modeled at 250m resolution. Neither represents localized field micro-topography.",
        "<b>Decision Support Boundary:</b> FieldShift provides agronomic scenario comparison and risk screening, NOT guaranteed yield forecasts or revenue warranties.",
        "<b>Agronomic Consultation:</b> All rotation recommendations must be verified with regional agricultural extension services and certified local agronomists.",
        "<b>Data Attributions:</b> NASA POWER Agroclimatology (NASA Langley Research Center); ISRIC SoilGrids 250m (ISRIC World Soil Information); FAO Drainage Papers 56 & 33 (United Nations Food and Agriculture Organization); NASA GIBS / ESDIS Worldview (Visual Basemap)."
    ]
    for lim in limitations:
        story.append(Paragraph(f"• {lim}", bullet_style))

    doc.build(story)
    return buffer.getvalue()

def generate_csv_export(farm_name: str, coords: tuple, climate_data: dict, soil_data: dict, rotations: list) -> str:
    """
    Serializes climate, soil, and top rotation alternatives into clean CSV string.
    """
    rows = []
    # Climate and Soil rows
    rows.append({"Category": "Metadata", "Parameter": "Farm Sector", "Value": farm_name})
    rows.append({"Category": "Metadata", "Parameter": "Latitude", "Value": coords[0]})
    rows.append({"Category": "Metadata", "Parameter": "Longitude", "Value": coords[1]})
    rows.append({"Category": "Soil", "Parameter": "Clay Percentage", "Value": soil_data.get("clay_pct")})
    rows.append({"Category": "Soil", "Parameter": "Sand Percentage", "Value": soil_data.get("sand_pct")})
    rows.append({"Category": "Soil", "Parameter": "Soil Organic Carbon (%)", "Value": soil_data.get("soc_pct")})
    rows.append({"Category": "Soil", "Parameter": "Soil pH", "Value": soil_data.get("ph")})
    rows.append({"Category": "Climate", "Parameter": "Mean Annual Rainfall (mm)", "Value": climate_data.get("mean_annual_rainfall_mm")})
    rows.append({"Category": "Climate", "Parameter": "10-Yr Rainfall Trend (%)", "Value": climate_data.get("rainfall_trend_pct")})
    rows.append({"Category": "Climate", "Parameter": "Warming Rate (C/decade)", "Value": climate_data.get("warming_rate_c_decade")})
    rows.append({"Category": "Climate", "Parameter": "Annual Hot Days (>35C)", "Value": climate_data.get("hot_days_per_year")})
    rows.append({"Category": "Climate", "Parameter": "Annual Dry Spells (>14d)", "Value": climate_data.get("dry_spells_per_year")})

    for i, r in enumerate(rotations):
        prefix = f"Rotation_Rank_{i+1}"
        rows.append({"Category": prefix, "Parameter": "Sequence", "Value": " -> ".join(r["crops"])})
        rows.append({"Category": prefix, "Parameter": "Composite Score", "Value": r["composite_score"]})
        rows.append({"Category": prefix, "Parameter": "Water Score", "Value": r["s_water"]})
        rows.append({"Category": prefix, "Parameter": "Soil Score", "Value": r["s_soil"]})
        rows.append({"Category": prefix, "Parameter": "Economic Score", "Value": r["s_econ"]})
        rows.append({"Category": prefix, "Parameter": "Resilience Score", "Value": r["s_resilience"]})
        rows.append({"Category": prefix, "Parameter": "Annual Water Need (mm)", "Value": r["annual_water_need_mm"]})
        rows.append({"Category": prefix, "Parameter": "Rationale", "Value": r["rationale"]})

    df = pd.DataFrame(rows)
    return df.to_csv(index=False)

def generate_json_export(farm_name: str, coords: tuple, climate_data: dict, soil_data: dict, past_crops: list, weights: dict, rotations: list, baseline_monoculture: dict, active_scenario: dict = None) -> str:
    """
    Serializes complete structured analysis payload into formatted JSON.
    """
    payload = {
        "generator": "FieldShift Tactical Rotation Advisor (NASA Space Apps 2026)",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "target_farm": {
            "name": farm_name,
            "latitude": coords[0],
            "longitude": coords[1]
        },
        "cropping_history": {
            "season_minus_2": past_crops[0],
            "season_minus_1": past_crops[1]
        },
        "tactical_priority_weights": weights,
        "isric_soil_profile": soil_data,
        "nasa_power_climate_indicators": climate_data,
        "baseline_monoculture_comparison": baseline_monoculture,
        "recommended_rotations": rotations,
        "active_climate_scenario": active_scenario,
        "provenance_statement": {
            "nasa_power": "NASA Langley Research Center POWER Daily Agroclimatology (2010-2024)",
            "isric_soilgrids": "ISRIC World Soil Information 250m REST API (0-30cm Depth)",
            "nasa_gibs": "NASA GIBS / ESDIS Worldview True Color & Blue Marble (Visual Basemap Only)",
            "disclaimer": "Decision-support risk assessment. Does not replace professional on-farm agronomic testing."
        }
    }
    return json.dumps(payload, indent=2)
