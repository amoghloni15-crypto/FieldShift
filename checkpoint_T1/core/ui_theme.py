"""
FieldShift Tactical UI Theme & Shared HUD Design System.
Provides Tron / Batcomputer / Holographic styling, provenance chips, and component helpers.
"""

import os
import streamlit as st

def render_html(html_str: str, sidebar: bool = False):
    """
    Strips leading/trailing indentation and empty lines to prevent Markdown
    from misinterpreting raw HTML as indented code blocks.
    """
    clean_lines = [line.strip() for line in html_str.splitlines() if line.strip()]
    cleaned = "\n".join(clean_lines)
    target = st.sidebar if sidebar else st
    if hasattr(target, "html"):
        target.html(cleaned)
    else:
        target.markdown(cleaned, unsafe_allow_html=True)

def inject_vault_styles():
    """
    Injects Google Fonts (Orbitron, Rajdhani, Share Tech Mono) and styles.css into the page.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    styles_path = os.path.join(base_dir, "styles.css")
    if os.path.exists(styles_path):
        with open(styles_path, "r", encoding="utf-8") as f:
            css_content = f.read()
            render_html(f"<style>{css_content}</style>")

def render_provenance_badge(badge_type: str, details: str = None) -> str:
    """
    Renders standardized scientific data provenance chip:
    - LIVE API: Real-time API response from NASA POWER or ISRIC
    - DERIVED: Mathematical indicator computed from verified data
    - MODELED / SIMULATED: Algorithmic output or sensitivity scenario
    - FARMER INPUT: Explicit user field override or priority setting
    - APPROXIMATE TABLE: Static agronomic parameter (FAO-56/FAO-33)
    - FALLBACK DEMO DATA: Verified regional baseline when network offline
    """
    badge_colors = {
        "LIVE API": {"bg": "rgba(44, 255, 176, 0.14)", "border": "#2CFFB0", "color": "#2CFFB0", "icon": "🛰️"},
        "DERIVED": {"bg": "rgba(25, 243, 255, 0.14)", "border": "#19F3FF", "color": "#19F3FF", "icon": "⚡"},
        "MODELED / SIMULATED": {"bg": "rgba(255, 158, 31, 0.14)", "border": "#FF9E1F", "color": "#FF9E1F", "icon": "🔮"},
        "FARMER INPUT": {"bg": "rgba(150, 100, 255, 0.16)", "border": "#B085FF", "color": "#C9A9FF", "icon": "👤"},
        "APPROXIMATE TABLE": {"bg": "rgba(255, 215, 0, 0.12)", "border": "#FFD700", "color": "#FFD700", "icon": "📖"},
        "FALLBACK DEMO DATA": {"bg": "rgba(255, 80, 80, 0.14)", "border": "#FF5050", "color": "#FF8080", "icon": "⚠️"}
    }
    
    cfg = badge_colors.get(badge_type, {"bg": "rgba(25, 243, 255, 0.12)", "border": "#19F3FF", "color": "#19F3FF", "icon": "ℹ️"})
    detail_html = f" <span style='opacity: 0.8; font-size: 0.68rem; margin-left: 4px;'>({details})</span>" if details else ""
    
    return f"""<span style="display: inline-flex; align-items: center; gap: 5px; background: {cfg['bg']}; border: 1px solid {cfg['border']}; color: {cfg['color']}; padding: 3px 9px; border-radius: 4px; font-family: 'Share Tech Mono', monospace; font-size: 0.72rem; letter-spacing: 0.8px; text-transform: uppercase; box-shadow: 0 0 8px {cfg['bg']};">{cfg['icon']} {badge_type}{detail_html}</span>"""

def render_command_bar(title: str, subtitle: str, status_chips: list = None):
    """
    Renders top tactical header bar with title, subtitle, and dynamic status telemetry chips.
    """
    chips_html = ""
    if status_chips:
        chips_str = "".join(status_chips)
        chips_html = f"""<div class="status-chip-container">{chips_str}</div>"""
        
    html = f"""
    <div class="command-bar">
      <div>
        <div class="command-title">{title}</div>
        <div class="command-subtitle">{subtitle}</div>
      </div>
      {chips_html}
    </div>
    """
    render_html(html)

def apply_vault_plotly_theme(fig, title: str = ""):
    """
    Applies unified Tron/HUD dark theme styling to Plotly graphs.
    """
    fig.update_layout(
        title=dict(
            text=f"<span style='font-family: Orbitron; color: #19F3FF; font-size: 14px; letter-spacing: 1px;'>// {title}</span>",
            x=0.02,
            y=0.96
        ),
        paper_bgcolor="#0A1118",
        plot_bgcolor="#070D14",
        font=dict(family="Rajdhani, sans-serif", color="#E8F6FF", size=13),
        xaxis=dict(
            gridcolor="rgba(25, 243, 255, 0.08)",
            linecolor="rgba(25, 243, 255, 0.3)",
            tickfont=dict(family="Share Tech Mono", color="#8FA6B8", size=11),
            zerolinecolor="rgba(25, 243, 255, 0.2)"
        ),
        yaxis=dict(
            gridcolor="rgba(25, 243, 255, 0.08)",
            linecolor="rgba(25, 243, 255, 0.3)",
            tickfont=dict(family="Share Tech Mono", color="#8FA6B8", size=11),
            zerolinecolor="rgba(25, 243, 255, 0.2)"
        ),
        margin=dict(l=30, r=30, t=55, b=30)
    )
    return fig

def render_arc_gauge(score: float, label: str, color: str = "#19F3FF"):
    """
    Renders arc-reactor circular gauge in pure HTML/CSS.
    """
    pct = max(0, min(100, int(score)))
    deg = int(pct * 3.6)
    return f"""<div class="arc-gauge-container"><div class="arc-gauge" style="background: conic-gradient({color} 0deg {deg}deg, rgba(25, 243, 255, 0.08) {deg}deg 360deg);"><div class="arc-gauge-inner"><div class="arc-score" style="color: {color};">{pct}</div></div></div><div class="arc-label">{label}</div></div>"""

def render_empty_analysis_notice():
    """
    Renders tactical reminder when a subpage is accessed before running analysis on Mission Control.
    """
    html = """
    <div style="background: rgba(10, 17, 24, 0.95); border: 1px solid rgba(255, 158, 31, 0.5); border-radius: 8px; padding: 24px 28px; margin: 2rem 0; box-shadow: 0 0 25px rgba(255, 158, 31, 0.15);">
      <div style="font-family: 'Orbitron', monospace; font-size: 1.1rem; color: #FF9E1F; letter-spacing: 1.5px; text-transform: uppercase;">
        ⚠️ TACTICAL INTEL NOT YET INITIALIZED
      </div>
      <div style="font-family: 'Rajdhani', sans-serif; font-size: 1rem; color: #E8F6FF; margin: 10px 0 16px 0; line-height: 1.5;">
        This intelligence module requires active agroclimatological and soil data from a selected farm. Please return to <strong>MISSION CONTROL</strong>, confirm your target sector and cropping history, and execute the analysis engine.
      </div>
    </div>
    """
    render_html(html)
