import os
import textwrap
from datetime import datetime
import httpx
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Weather Forecast & Alert Dashboard",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------
# Custom Styling: Dark Emerald Palette & Rounded Cards
# ---------------------------------------------------------
st.markdown(
    """
    <style>
    /* Global dark emerald background */
    .stApp {
        background-color: #060e0a !important;
        color: #e2f1e8 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Hide Streamlit header/footer noise */
    #MainMenu, footer, header, [data-testid="stToolbar"], [data-testid="stDecoration"] {
        visibility: hidden !important;
        height: 0 !important;
    }
    
    .block-container {
        padding-top: 1.2rem !important;
        padding-bottom: 2rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 1500px !important;
    }

    /* Emerald cards styling */
    .emerald-card {
        background: linear-gradient(145deg, #0d2619 0%, #081a11 100%);
        border: 1px solid rgba(46, 125, 85, 0.35);
        border-radius: 20px;
        padding: 22px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.45);
        margin-bottom: 18px;
        position: relative;
        overflow: hidden;
    }

    .emerald-card-subtle {
        background: rgba(14, 38, 26, 0.65);
        border: 1px solid rgba(46, 125, 85, 0.25);
        border-radius: 16px;
        padding: 16px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
    }

    /* Left Nav Rail styling */
    .nav-rail {
        display: flex;
        flex-direction: column;
        align-items: center;
        background: #091b12;
        border: 1px solid rgba(46, 125, 85, 0.3);
        border-radius: 24px;
        padding: 20px 8px;
        gap: 22px;
        height: 100%;
        min-height: 520px;
    }
    .nav-icon {
        width: 42px;
        height: 42px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 12px;
        color: #7fa691;
        font-size: 1.25rem;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    .nav-icon:hover, .nav-icon.active {
        background: rgba(34, 197, 94, 0.2);
        color: #34d399;
        border: 1px solid rgba(52, 211, 153, 0.4);
    }
    .nav-icon-bottom {
        margin-top: auto;
    }

    /* Custom button styling */
    div.stButton > button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: #ffffff !important;
        border: 1px solid rgba(52, 211, 153, 0.4) !important;
        border-radius: 20px !important;
        font-weight: 600 !important;
        padding: 6px 20px !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button:hover {
        background: #34d399 !important;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4) !important;
        color: #062415 !important;
    }

    /* Style text input */
    div[data-baseweb="input"] {
        background-color: #0d2619 !important;
        border-radius: 20px !important;
        border: 1px solid rgba(52, 211, 153, 0.3) !important;
    }
    div[data-baseweb="input"] input {
        color: #e2f1e8 !important;
        font-size: 0.95rem !important;
    }

    /* Style radio group (C/F toggle) */
    div[data-testid="stRadio"] > div {
        background: #0d2619 !important;
        border-radius: 20px !important;
        border: 1px solid rgba(52, 211, 153, 0.3) !important;
        padding: 4px 12px !important;
        display: flex;
        gap: 12px;
    }
    div[data-testid="stRadio"] label {
        color: #a7f3d0 !important;
        font-weight: 600 !important;
    }
    .top-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
        margin-bottom: 20px;
        flex-wrap: wrap;
    }

    .pill-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: #0d2619;
        border: 1px solid rgba(52, 211, 153, 0.3);
        border-radius: 24px;
        padding: 6px 16px;
        font-size: 0.88rem;
        color: #d1fae5;
        font-weight: 500;
    }

    .pill-badge-sim {
        background: rgba(245, 158, 11, 0.15);
        border: 1px solid rgba(245, 158, 11, 0.4);
        color: #fbbf24;
    }

    .pill-badge-live {
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid rgba(16, 185, 129, 0.4);
        color: #34d399;
    }

    /* Weather condition typography */
    .temp-huge {
        font-size: 4.6rem;
        font-weight: 700;
        line-height: 1;
        color: #ffffff;
        letter-spacing: -1.5px;
    }
    .temp-feels {
        color: #94bba7;
        font-size: 1.05rem;
        margin-top: 6px;
    }
    .weather-condition-text {
        font-size: 1.45rem;
        font-weight: 600;
        color: #e6f7ef;
        margin-top: 10px;
    }
    .weather-high-low {
        color: #94bba7;
        font-size: 0.95rem;
        margin-top: 14px;
    }

    /* Highlight compact cards */
    .highlight-card {
        background: #0b2216;
        border: 1px solid rgba(46, 125, 85, 0.3);
        border-radius: 16px;
        padding: 16px;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .highlight-title {
        font-size: 0.85rem;
        font-weight: 500;
        color: #7fa691;
        margin-bottom: 6px;
    }
    .highlight-val {
        font-size: 1.65rem;
        font-weight: 700;
        color: #ffffff;
    }
    .highlight-sub {
        font-size: 0.8rem;
        color: #94bba7;
        margin-top: 4px;
    }

    /* Mini rain bar meters */
    .mini-bar-container {
        display: flex;
        align-items: flex-end;
        gap: 6px;
        height: 64px;
        margin-top: 8px;
    }
    .mini-bar-item {
        flex: 1;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: flex-end;
        align-items: center;
        gap: 4px;
    }
    .mini-bar {
        width: 100%;
        height: 48px;
        background: #143d28;
        border-radius: 4px;
        position: relative;
        display: flex;
        align-items: flex-end;
    }
    .mini-bar-fill {
        background: #34d399;
        border-radius: 4px;
        width: 100%;
    }
    .mini-bar-label {
        color: #7fa691;
        font-size: 0.62rem;
        line-height: 1;
    }

    /* Alert cards distinction */
    .alert-box {
        border-radius: 12px;
        padding: 12px 14px;
        margin-bottom: 8px;
        font-size: 0.88rem;
        line-height: 1.35;
        display: flex;
        align-items: flex-start;
        gap: 10px;
    }
    .alert-critical {
        background: rgba(220, 38, 38, 0.16);
        border: 1px solid rgba(239, 68, 68, 0.6);
        color: #fca5a5;
    }
    .alert-warning {
        background: rgba(217, 119, 6, 0.18);
        border: 1px solid rgba(245, 158, 11, 0.6);
        color: #fde68a;
    }
    .alert-info {
        background: rgba(6, 182, 212, 0.15);
        border: 1px solid rgba(6, 182, 212, 0.4);
        color: #a5f3fc;
    }
    .alert-clear {
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid rgba(16, 185, 129, 0.4);
        color: #6ee7b7;
    }

    /* Hourly pill item */
    .hourly-pill {
        background: #0b2216;
        border: 1px solid rgba(46, 125, 85, 0.3);
        border-radius: 20px;
        padding: 12px 8px;
        text-align: center;
        min-width: 65px;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 6px;
    }
    .hourly-time {
        font-size: 0.78rem;
        color: #7fa691;
    }
    .hourly-temp {
        font-size: 0.95rem;
        font-weight: 600;
        color: #ffffff;
    }

    /* Other city cards */
    .other-city-card {
        background: #0b2216;
        border: 1px solid rgba(46, 125, 85, 0.3);
        border-radius: 16px;
        padding: 14px 18px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 10px;
        transition: transform 0.15s ease, border-color 0.15s ease;
    }
    .other-city-card:hover {
        border-color: rgba(52, 211, 153, 0.6);
        transform: translateY(-2px);
    }

    /* Responsive adjustments */
    @media (max-width: 900px) {
        .block-container {
            padding-left: 0.8rem !important;
            padding-right: 0.8rem !important;
        }
        .temp-huge {
            font-size: 3.2rem;
        }
        .nav-rail {
            flex-direction: row;
            height: auto;
            min-height: auto;
            padding: 10px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# Helper Functions: WMO Mapping, Units, Graphics
# ---------------------------------------------------------
WMO_MAP = {
    0: ("Clear Sky", "☀️", "#f59e0b"),
    1: ("Mainly Clear", "🌤️", "#fbbf24"),
    2: ("Partly Cloudy", "⛅", "#34d399"),
    3: ("Overcast", "☁️", "#94bba7"),
    45: ("Foggy", "🌫️", "#6ee7b7"),
    48: ("Freezing Fog", "🌫️", "#a7f3d0"),
    51: ("Light Drizzle", "🌦️", "#38bdf8"),
    53: ("Drizzle", "🌦️", "#38bdf8"),
    55: ("Dense Drizzle", "🌧️", "#0ea5e9"),
    61: ("Slight Rain", "🌧️", "#38bdf8"),
    63: ("Moderate Rain", "🌧️", "#0ea5e9"),
    65: ("Heavy Rain", "🌧️", "#0284c7"),
    71: ("Light Snow", "🌨️", "#e0f2fe"),
    73: ("Snow Fall", "🌨️", "#e0f2fe"),
    75: ("Heavy Snow", "❄️", "#bae6fd"),
    77: ("Snow Grains", "❄️", "#bae6fd"),
    80: ("Rain Showers", "🌦️", "#38bdf8"),
    81: ("Heavy Showers", "🌧️", "#0ea5e9"),
    82: ("Violent Showers", "⛈️", "#6366f1"),
    85: ("Snow Showers", "🌨️", "#e0f2fe"),
    86: ("Heavy Snow Showers", "❄️", "#bae6fd"),
    95: ("Thunderstorm", "⛈️", "#f59e0b"),
    96: ("Thunderstorm w/ Hail", "⛈️", "#ef4444"),
    99: ("Severe Hailstorm", "⛈️", "#dc2626"),
}


def get_wmo_info(code: int | None):
    if code is None:
        return ("Unknown", "🌦️", "#34d399")
    return WMO_MAP.get(int(code), ("Fair Weather", "🌤️", "#34d399"))


def convert_temp(val_c: float | None, unit: str) -> str:
    if val_c is None:
        return "—"
    if unit == "°F":
        return f"{round((val_c * 9/5) + 32)}°F"
    return f"{round(val_c)}°C"


def convert_temp_val(val_c: float | None, unit: str) -> float | None:
    if val_c is None:
        return None
    if unit == "°F":
        return round((val_c * 9/5) + 32, 1)
    return round(val_c, 1)


def format_clock_time(iso_or_time: str | None) -> str:
    if not iso_or_time:
        return "Unavailable"
    try:
        t_part = iso_or_time.split("T")[1][:5] if "T" in iso_or_time else iso_or_time[:5]
        hh, mm = map(int, t_part.split(":"))
        suffix = "AM" if hh < 12 else "PM"
        disp_h = hh % 12 or 12
        return f"{disp_h}:{mm:02d} {suffix}"
    except Exception:
        return str(iso_or_time)


def get_day_length(sunrise_str: str | None, sunset_str: str | None) -> str:
    if not sunrise_str or not sunset_str:
        return "Unavailable"
    try:
        t_rise = sunrise_str.split("T")[1][:5] if "T" in sunrise_str else sunrise_str[:5]
        t_set = sunset_str.split("T")[1][:5] if "T" in sunset_str else sunset_str[:5]
        hr_r, min_r = map(int, t_rise.split(":"))
        hr_s, min_s = map(int, t_set.split(":"))
        diff = (hr_s * 60 + min_s) - (hr_r * 60 + min_r)
        if diff < 0:
            diff += 24 * 60
        return f"{diff // 60} hr {diff % 60} min"
    except Exception:
        return "Unavailable"


def render_weather_svg(weather_code: int | None) -> str:
    """Generate inline SVG weather graphic for the main emerald card with zero newline indentation."""
    code = int(weather_code) if weather_code is not None else 2
    if code in {95, 96, 99}:
        # Thunderstorm with lightning
        return '<svg width="150" height="130" viewBox="0 0 150 130" fill="none" xmlns="http://www.w3.org/2000/svg"><defs><linearGradient id="cloudGrad" x1="20" y1="20" x2="110" y2="90" gradientUnits="userSpaceOnUse"><stop stop-color="#4a695b"/><stop offset="1" stop-color="#183626"/></linearGradient><filter id="glow" x="0" y="0" width="150" height="130" filterUnits="userSpaceOnUse"><feGaussianBlur stdDeviation="6" result="blur"/><feComposite in="SourceGraphic" in2="blur" operator="over"/></filter></defs><path d="M45 40a25 25 0 0148-8 20 20 0 0122 18 20 20 0 01-4 38H35a22 22 0 01-3-43 25 25 0 0113-5z" fill="url(#cloudGrad)"/><path d="M68 65l-14 26h16l-8 26 26-32h-16l10-20z" fill="#facc15" filter="url(#glow)"/></svg>'
    elif code in {0, 1}:
        # Clear / Glowing Sun
        return '<svg width="150" height="130" viewBox="0 0 150 130" fill="none" xmlns="http://www.w3.org/2000/svg"><defs><radialGradient id="sunGrad" cx="75" cy="65" r="35" gradientUnits="userSpaceOnUse"><stop stop-color="#fef08a"/><stop offset="0.6" stop-color="#f59e0b"/><stop offset="1" stop-color="#d97706"/></radialGradient><filter id="sunGlow" x="15" y="5" width="120" height="120" filterUnits="userSpaceOnUse"><feGaussianBlur stdDeviation="8" result="blur"/><feComposite in="SourceGraphic" in2="blur" operator="over"/></filter></defs><circle cx="75" cy="65" r="32" fill="url(#sunGrad)" filter="url(#sunGlow)"/><g stroke="#f59e0b" stroke-width="3" stroke-linecap="round"><line x1="75" y1="18" x2="75" y2="28" /><line x1="75" y1="102" x2="75" y2="112" /><line x1="28" y1="65" x2="38" y2="65" /><line x1="112" y1="65" x2="122" y2="65" /><line x1="42" y1="32" x2="49" y2="39" /><line x1="101" y1="91" x2="108" y2="98" /><line x1="42" y1="98" x2="49" y2="91" /><line x1="101" y1="39" x2="108" y2="32" /></g></svg>'
    elif code in {51, 53, 55, 61, 63, 65, 80, 81, 82}:
        # Rain Cloud
        return '<svg width="150" height="130" viewBox="0 0 150 130" fill="none" xmlns="http://www.w3.org/2000/svg"><defs><linearGradient id="rainCloud" x1="20" y1="20" x2="110" y2="90" gradientUnits="userSpaceOnUse"><stop stop-color="#3b6b57"/><stop offset="1" stop-color="#143324"/></linearGradient></defs><path d="M42 38a24 24 0 0146-8 19 19 0 0121 17 19 19 0 01-4 36H32a21 21 0 01-3-41 24 24 0 0113-4z" fill="url(#rainCloud)"/><g stroke="#38bdf8" stroke-width="3" stroke-linecap="round"><line x1="45" y1="92" x2="38" y2="108" /><line x1="65" y1="92" x2="58" y2="108" /><line x1="85" y1="92" x2="78" y2="108" /><line x1="105" y1="92" x2="98" y2="108" /></g></svg>'
    else:
        # Partly cloudy (Sun peeking behind cloud - reference look)
        return '<svg width="150" height="130" viewBox="0 0 150 130" fill="none" xmlns="http://www.w3.org/2000/svg"><defs><radialGradient id="sunPart" cx="95" cy="42" r="28" gradientUnits="userSpaceOnUse"><stop stop-color="#fef08a"/><stop offset="0.7" stop-color="#f59e0b"/></radialGradient><linearGradient id="cloudPart" x1="20" y1="35" x2="110" y2="105" gradientUnits="userSpaceOnUse"><stop stop-color="#558872"/><stop offset="1" stop-color="#1c3e2e"/></linearGradient><filter id="aura" x="60" y="8" width="70" height="70" filterUnits="userSpaceOnUse"><feGaussianBlur stdDeviation="5" result="blur"/><feComposite in="SourceGraphic" in2="blur" operator="over"/></filter></defs><circle cx="95" cy="42" r="24" fill="url(#sunPart)" filter="url(#aura)"/><g stroke="#f59e0b" stroke-width="2.5" stroke-linecap="round"><line x1="95" y1="8" x2="95" y2="14" /><line x1="126" y1="42" x2="132" y2="42" /><line x1="117" y1="20" x2="122" y2="15" /><line x1="117" y1="64" x2="122" y2="69" /></g><path d="M40 50a26 26 0 0150-8 20 20 0 0122 18 20 20 0 01-4 39H30a23 23 0 01-3-45 26 26 0 0113-4z" fill="url(#cloudPart)"/></svg>'


# ---------------------------------------------------------
# State & Data Fetching
# ---------------------------------------------------------
api_url = os.getenv("WEATHER_API_URL", "http://127.0.0.1:8000")

if "unit" not in st.session_state:
    st.session_state.unit = "°C"
if "selected_city_index" not in st.session_state:
    st.session_state.selected_city_index = 0

# ---------------------------------------------------------
# Top Bar: Search, Location Indicator, Unit Switch
# ---------------------------------------------------------
top_col1, top_col2, top_col3 = st.columns([5.5, 3.5, 3.0])

with top_col1:
    search_query = st.text_input(
        "Search City",
        value="Delhi, Mumbai",
        placeholder="Enter city names, e.g. Delhi, Mumbai, London...",
        label_visibility="collapsed",
    )

with top_col2:
    fetch_clicked = st.button("🔍 Fetch Weather", type="primary", use_container_width=True)

with top_col3:
    unit_choice = st.radio(
        "Temperature Unit",
        options=["°C", "°F"],
        index=0 if st.session_state.unit == "°C" else 1,
        horizontal=True,
        label_visibility="collapsed",
    )
    st.session_state.unit = unit_choice

# Trigger API load
if fetch_clicked or "reports" not in st.session_state:
    names = [c.strip() for c in search_query.split(",") if c.strip()]
    if not names:
        names = ["Delhi"]
    try:
        resp = httpx.get(
            f"{api_url}/weather",
            params=[("cities", name) for name in names],
            timeout=30,
        )
        resp.raise_for_status()
        st.session_state.reports = resp.json()
        st.session_state.selected_city_index = 0
    except Exception as exc:
        st.error(f"Could not reach API at {api_url}: {exc}")
        st.stop()

reports = st.session_state.get("reports", [])
if not reports:
    st.warning("No weather reports available.")
    st.stop()

# Safety bound check
if st.session_state.selected_city_index >= len(reports):
    st.session_state.selected_city_index = 0

active_idx = st.session_state.selected_city_index
active_report = reports[active_idx]
unit = st.session_state.unit

# ---------------------------------------------------------
# Subheader Badge Line: Mode, Source, Observation Time
# ---------------------------------------------------------
is_demo = "simulat" in active_report.get("source", "").lower()
badge_class = "pill-badge-sim" if is_demo else "pill-badge-live"
badge_text = "🟠 Demo Mode (Simulated Data)" if is_demo else "🟢 Live Data (Open-Meteo)"

obs_time = active_report.get("observed_at", "")
try:
    if "T" in obs_time:
        obs_formatted = datetime.fromisoformat(obs_time.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M UTC")
    else:
        obs_formatted = obs_time
except Exception:
    obs_formatted = str(obs_time)

st.markdown(
    f"""
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px; flex-wrap:wrap; gap:10px;">
        <div style="display:flex; gap:10px; align-items:center;">
            <span class="pill-badge {badge_class}">{badge_text}</span>
            <span class="pill-badge">📍 {active_report['location']}</span>
        </div>
        <div style="color:#7fa691; font-size:0.85rem;">
            Observed: <strong>{obs_formatted}</strong> · Timezone: <strong>{active_report.get('timezone', 'UTC')}</strong>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# Main Dashboard Grid: Left Rail + Center Cards + Right Highlights
# ---------------------------------------------------------
rail_col, center_col, right_col = st.columns([0.65, 5.85, 5.5])

# Left Navigation Rail
with rail_col:
    st.markdown(
        """
        <div class="nav-rail">
            <div class="nav-icon active" title="Dashboard">⊞</div>
            <div class="nav-icon" title="Locations">📍</div>
            <div class="nav-icon" title="Weather Outlook">☁️</div>
            <div class="nav-icon" title="Active Alerts">⚡</div>
            <div class="nav-icon" title="Settings">⚙️</div>
            <div class="nav-icon nav-icon-bottom" title="API Status">ℹ️</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Center Column: Main Weather Card & Today/Week Forecast Outlook
with center_col:
    current = active_report.get("current", {})
    weather_code = current.get("weather_code")
    cond_name, cond_emoji, cond_color = get_wmo_info(weather_code)
    temp_c = current.get("temperature_c")
    feels_c = current.get("feels_like_c")
    forecast_days = active_report.get("forecast", [])
    today_fc = forecast_days[0] if forecast_days else {}
    high_c = today_fc.get("temperature_max_c")
    low_c = today_fc.get("temperature_min_c")

    # 1. Main Weather Card
    svg_graphic = render_weather_svg(weather_code)
    st.markdown(
        f"""<div class="emerald-card">
<div style="display:flex; justify-content:space-between; align-items:flex-start;">
<div>
<div class="pill-badge" style="margin-bottom:16px;">📍 {active_report['location']}</div>
<div style="color:#7fa691; font-size:0.95rem; font-weight:500;">Weather · Now</div>
<div class="weather-condition-text">{cond_emoji} {cond_name}</div>
<div class="temp-huge" style="margin-top:14px;">{convert_temp(temp_c, unit)}</div>
<div class="temp-feels">Feels like {convert_temp(feels_c, unit)}</div>
<div class="weather-high-low">High: <strong style="color:#ffffff;">{convert_temp(high_c, unit)}</strong> &nbsp;·&nbsp; Low: <strong style="color:#ffffff;">{convert_temp(low_c, unit)}</strong></div>
</div>
<div style="margin-top:10px;">{svg_graphic}</div>
</div>
</div>""",
        unsafe_allow_html=True,
    )

    # 2. Bottom Outlook Card: Hourly Forecast + Sun & Day Length Box
    st.markdown(
        """
        <div class="emerald-card" style="padding-bottom:18px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
                <div style="font-size:1.15rem; font-weight:600; color:#ffffff;">
                    Today / Week
                </div>
                <div style="font-size:0.85rem; color:#7fa691;">
                    Hourly Progression
                </div>
            </div>
        """,
        unsafe_allow_html=True,
    )

    # Hourly cards row
    hourly_data = active_report.get("hourly", [])
    if hourly_data:
        h_cols = st.columns(min(6, len(hourly_data)))
        for i, h_col in enumerate(h_cols):
            h_entry = hourly_data[i]
            h_code = h_entry.get("weather_code")
            _, h_icon, _ = get_wmo_info(h_code)
            h_temp = convert_temp(h_entry.get("temperature_c"), unit)
            h_time = format_clock_time(h_entry.get("time"))
            with h_col:
                st.markdown(
                    f"""
                    <div class="hourly-pill">
                        <div class="hourly-time">{h_time}</div>
                        <div style="font-size:1.35rem;">{h_icon}</div>
                        <div class="hourly-temp">{h_temp}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    else:
        st.markdown(
            """
            <div style="color:#7fa691; font-size:0.88rem; padding:10px 0;">
                Hourly forecast data: <em>Unavailable</em>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Sunrise, Sunset & Day Length
    sunrise_val = today_fc.get("sunrise")
    sunset_val = today_fc.get("sunset")
    sunrise_fmt = format_clock_time(sunrise_val)
    sunset_fmt = format_clock_time(sunset_val)
    day_len_fmt = get_day_length(sunrise_val, sunset_val)

    # Tomorrow highlight
    tomorrow_fc = forecast_days[1] if len(forecast_days) > 1 else {}
    tmrw_code = tomorrow_fc.get("weather_code")
    tmrw_name, tmrw_icon, _ = get_wmo_info(tmrw_code)
    tmrw_high = convert_temp(tomorrow_fc.get("temperature_max_c"), unit)

    st.markdown(
        f"""<div style="display:flex; justify-content:space-between; gap:14px; margin-top:20px; flex-wrap:wrap;">
<div class="emerald-card-subtle" style="flex:1; min-width:210px;">
<div style="color:#7fa691; font-size:0.8rem; margin-bottom:6px;">Tomorrow</div>
<div style="font-size:1.1rem; font-weight:600; color:#ffffff;">{tmrw_icon} {tmrw_name}</div>
<div style="font-size:1.35rem; font-weight:700; color:#34d399; margin-top:4px;">{tmrw_high}</div>
</div>
<div class="emerald-card-subtle" style="flex:1.4; min-width:240px; display:flex; justify-content:space-between; align-items:center;">
<div>
<div style="color:#7fa691; font-size:0.78rem;">Sunrise</div>
<div style="font-size:1.05rem; font-weight:600; color:#fde68a;">🌅 {sunrise_fmt}</div>
</div>
<div>
<div style="color:#7fa691; font-size:0.78rem;">Sunset</div>
<div style="font-size:1.05rem; font-weight:600; color:#fb923c;">🌇 {sunset_fmt}</div>
</div>
<div>
<div style="color:#7fa691; font-size:0.78rem;">Day Length</div>
<div style="font-size:0.95rem; font-weight:600; color:#a7f3d0;">⏱️ {day_len_fmt}</div>
</div>
</div>
</div>
</div>""",
        unsafe_allow_html=True,
    )


# Right Column: Today's Highlights & Other Cities
with right_col:
    st.markdown(
        """
        <div style="font-size:1.25rem; font-weight:600; color:#ffffff; margin-bottom:14px;">
            Today's Highlight
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Grid of Highlights (2 rows x 2 columns)
    hl_row1_col1, hl_row1_col2 = st.columns(2)
    hl_row2_col1, hl_row2_col2 = st.columns(2)

    # 1. Chances of Rain
    rain_chance = int(today_fc.get("precipitation_probability_max", 0)) if today_fc else 0
    rain_bars = "".join(
        f"""<div class=\"mini-bar-item\" title=\"Day {i + 1}: {int(day.get('precipitation_probability_max') or 0)}%\">
<div class=\"mini-bar\"><div class=\"mini-bar-fill\" style=\"height:{max(0, min(100, int(day.get('precipitation_probability_max') or 0)))}%;\"></div></div>
<div class=\"mini-bar-label\">D{i + 1}</div>
</div>"""
        for i, day in enumerate(forecast_days[:5])
    )
    with hl_row1_col1:
        st.markdown(
            f"""
            <div class="highlight-card">
                <div>
                    <div class="highlight-title">Chances of Rain</div>
                    <div class="highlight-val">{rain_chance}%</div>
                </div>
                <div class="mini-bar-container">
                    {rain_bars or '<div class="highlight-sub">Forecast unavailable</div>'}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 2. UV Index
    uv_raw = current.get("uv_index") or today_fc.get("uv_index_max")
    if uv_raw is not None:
        uv_num = float(uv_raw)
        uv_cat = "Low" if uv_num < 3 else ("Moderate" if uv_num < 6 else ("High" if uv_num < 8 else "Very High"))
        uv_display = f"{uv_num:.1f} / 10"
    else:
        uv_cat = ""
        uv_display = "Unavailable"

    with hl_row1_col2:
        st.markdown(
            f"""
            <div class="highlight-card">
                <div>
                    <div class="highlight-title">UV Index</div>
                    <div class="highlight-val">{uv_display}</div>
                    <div class="highlight-sub">{uv_cat}</div>
                </div>
                <div style="margin-top:14px; background:#143d28; border-radius:10px; height:8px; overflow:hidden;">
                    <div style="background:#f59e0b; width:{min(100, int(float(uv_raw or 0) * 10))}%; height:100%; border-radius:10px;"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 3. Wind Status
    wind_kmh = float(current.get("wind_speed_kmh") or 0)
    wind_disp = f"{round(wind_kmh * 0.621371, 1)} mph" if unit == "°F" else f"{round(wind_kmh, 1)} km/h"
    with hl_row2_col1:
        st.markdown(
            f"""
            <div class="highlight-card">
                <div>
                    <div class="highlight-title">Wind Status</div>
                    <div class="highlight-val">{wind_disp}</div>
                </div>
                <div style="display:flex; align-items:center; gap:8px; margin-top:10px;">
                    <span style="font-size:1.3rem;">💨</span>
                    <span style="color:#7fa691; font-size:0.85rem;">Directional air flow</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 4. Humidity & Air Quality
    humidity_val = current.get("humidity_percent")
    hum_disp = f"{humidity_val}%" if humidity_val is not None else "Unavailable"
    hum_sub = "Oppressive" if (humidity_val or 0) >= 85 else ("Elevated" if (humidity_val or 0) >= 75 else "Comfortable")

    aqi_data = active_report.get("air_quality") or {}
    aqi_val = aqi_data.get("us_aqi")
    aqi_disp = f"US AQI {aqi_val}" if aqi_val is not None else "AQI Unavailable"

    with hl_row2_col2:
        st.markdown(
            f"""
            <div class="highlight-card">
                <div>
                    <div class="highlight-title">Humidity & AQI</div>
                    <div class="highlight-val">{hum_disp}</div>
                    <div class="highlight-sub">{hum_sub} · {aqi_disp}</div>
                </div>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-top:10px;">
                    <span style="font-size:1.3rem;">💧</span>
                    <span class="pill-badge" style="padding:2px 10px; font-size:0.75rem;">{hum_sub}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 5. Risk Alerts Highlight Box (Distinguishing Critical vs Warning vs Info)
    st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)
    alerts = active_report.get("alerts", [])
    st.markdown(
        """
        <div style="font-size:1.05rem; font-weight:600; color:#ffffff; margin-bottom:8px;">
            Risk Alerts
        </div>
        """,
        unsafe_allow_html=True,
    )
    if alerts:
        for alert in alerts:
            sev = alert.get("severity", "info")
            msg = alert.get("message", "")
            if sev == "critical":
                st.markdown(
                    f"""
                    <div class="alert-box alert-critical">
                        <span style="font-size:1.2rem;">🚨</span>
                        <div><strong>CRITICAL ALERT:</strong> {msg}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            elif sev == "warning":
                st.markdown(
                    f"""
                    <div class="alert-box alert-warning">
                        <span style="font-size:1.2rem;">⚠️</span>
                        <div><strong>WARNING:</strong> {msg}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                    <div class="alert-box alert-info">
                        <span style="font-size:1.2rem;">ℹ️</span>
                        <div><strong>INFO:</strong> {msg}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    else:
        st.markdown(
            """
            <div class="alert-box alert-clear">
                <span>✅</span>
                <div><strong>ALL CLEAR:</strong> No severe risks crossed configured thresholds.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 6. Other Cities Section
    st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="font-size:1.15rem; font-weight:600; color:#ffffff; margin-bottom:10px;">
            Other Cities
        </div>
        """,
        unsafe_allow_html=True,
    )

    other_indices = [i for i in range(len(reports)) if i != active_idx]
    if other_indices:
        for o_idx in other_indices:
            o_rep = reports[o_idx]
            o_curr = o_rep.get("current", {})
            o_wcode = o_curr.get("weather_code")
            o_cond, o_icon, _ = get_wmo_info(o_wcode)
            o_temp = convert_temp(o_curr.get("temperature_c"), unit)
            o_alert_cnt = len(o_rep.get("alerts", []))
            o_alert_txt = f"{o_alert_cnt} alert{'s' if o_alert_cnt != 1 else ''}" if o_alert_cnt else "No alerts"

            col_oc_info, col_oc_btn = st.columns([4, 1.5])
            with col_oc_info:
                st.markdown(
                    f"""
                    <div class="other-city-card">
                        <div>
                            <div style="font-weight:600; font-size:1.05rem; color:#ffffff;">{o_rep['location']}</div>
                            <div style="font-size:0.8rem; color:#7fa691; margin-top:2px;">{o_icon} {o_cond} · {o_alert_txt}</div>
                        </div>
                        <div style="font-size:1.5rem; font-weight:700; color:#34d399;">
                            {o_temp}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with col_oc_btn:
                if st.button("View", key=f"btn_switch_{o_idx}", use_container_width=True):
                    st.session_state.selected_city_index = o_idx
                    st.rerun()
    else:
        st.markdown(
            """
            <div class="emerald-card-subtle" style="font-size:0.85rem; color:#7fa691;">
                Query multiple cities separated by commas in the top bar (e.g. <code>Delhi, Mumbai, storm-demo</code>) to view and compare other locations side-by-side.
            </div>
            """,
            unsafe_allow_html=True,
        )

# ---------------------------------------------------------
# Lower Section: 7-Day Forecast Visualization & Geographic Map
# ---------------------------------------------------------
st.markdown("<hr style='border-color: rgba(46, 125, 85, 0.25); margin: 30px 0 20px 0;'>", unsafe_allow_html=True)
vis_tab1, vis_tab2, vis_tab3 = st.tabs(["📈 7-Day Forecast & Trends", "🗺️ Geographic Map & Comparison", "🔍 API Inspection"])

with vis_tab1:
    st.subheader(f"7-Day Weather Outlook — {active_report['location']}")
    if forecast_days:
        # Readable short-range 7-day forecast cards
        fc_cols = st.columns(min(7, len(forecast_days)))
        for i, f_col in enumerate(fc_cols):
            f_day = forecast_days[i]
            f_code = f_day.get("weather_code")
            _, f_icon, _ = get_wmo_info(f_code)
            f_high = convert_temp(f_day.get("temperature_max_c"), unit)
            f_low = convert_temp(f_day.get("temperature_min_c"), unit)
            f_rain = f_day.get("precipitation_probability_max", 0)
            f_date = f_day.get("date", f"Day +{i+1}")
            with f_col:
                st.markdown(
                    f"""<div class="emerald-card-subtle" style="text-align:center; padding:12px 6px;">
<div style="font-size:0.78rem; color:#7fa691; margin-bottom:4px;">{f_date}</div>
<div style="font-size:1.4rem;">{f_icon}</div>
<div style="font-size:0.95rem; font-weight:700; color:#ffffff; margin-top:4px;">{f_high}</div>
<div style="font-size:0.8rem; color:#7fa691;">{f_low}</div>
<div style="font-size:0.75rem; color:#38bdf8; margin-top:2px;">💧 {f_rain}%</div>
</div>""",
                    unsafe_allow_html=True,
                )
        st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)

        fc_df = pd.DataFrame(forecast_days)
        # Convert temperature values for chart if unit is Fahrenheit
        fc_df["temp_max_plot"] = fc_df["temperature_max_c"].apply(lambda v: convert_temp_val(v, unit))
        fc_df["temp_min_plot"] = fc_df["temperature_min_c"].apply(lambda v: convert_temp_val(v, unit))

        # Temperature Trend Plotly Line Chart
        fig_temp = px.line(
            fc_df,
            x="date",
            y=["temp_max_plot", "temp_min_plot"],
            markers=True,
            labels={"value": f"Temperature ({unit})", "variable": "Trend", "date": "Date"},
            color_discrete_map={"temp_max_plot": "#10b981", "temp_min_plot": "#38bdf8"},
        )
        fig_temp.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(11,34,22,0.45)",
            font={"color": "#e2f1e8"},
            legend={"title": ""},
            margin=dict(l=20, r=20, t=30, b=20),
            xaxis=dict(showgrid=True, gridcolor="rgba(46, 125, 85, 0.2)"),
            yaxis=dict(showgrid=True, gridcolor="rgba(46, 125, 85, 0.2)"),
        )
        st.plotly_chart(fig_temp, use_container_width=True, key=f"temperature-chart-{active_idx}")

        # Precipitation Bar Chart
        fig_rain = px.bar(
            fc_df,
            x="date",
            y="precipitation_probability_max",
            labels={"precipitation_probability_max": "Rain Chance (%)", "date": "Date"},
            color_discrete_sequence=["#059669"],
        )
        fig_rain.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(11,34,22,0.45)",
            font={"color": "#e2f1e8"},
            margin=dict(l=20, r=20, t=30, b=20),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="rgba(46, 125, 85, 0.2)"),
        )
        st.plotly_chart(fig_rain, use_container_width=True, key=f"precipitation-chart-{active_idx}")
    else:
        st.info("No 7-day forecast data returned.")

with vis_tab2:
    st.subheader("Selected Locations Map")
    map_frame = pd.DataFrame(
        [
            {
                "Location": r["location"],
                "Latitude": r["latitude"],
                "Longitude": r["longitude"],
                f"Temperature ({unit})": convert_temp(r["current"].get("temperature_c"), unit),
                "Wind (km/h)": r["current"].get("wind_speed_kmh"),
                "US AQI": (r.get("air_quality") or {}).get("us_aqi") or "Unavailable",
            }
            for r in reports
        ]
    )
    st.map(map_frame.rename(columns={"Latitude": "lat", "Longitude": "lon"}), latitude="lat", longitude="lon", size=60)
    st.dataframe(map_frame, hide_index=True, use_container_width=True)

with vis_tab3:
    st.subheader("Raw API Response Payload")
    st.json(active_report)
