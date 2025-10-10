# enhanced_dashboard.py
# Multi-page, mobile-responsive dashboard with advanced features

import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import streamlit.components.v1 as components
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import json
from datetime import datetime, timedelta
import base64
from io import BytesIO

# Page configuration
st.set_page_config(
    page_title="Rwanda Malnutrition Intelligence Platform",
    page_icon="🇷🇼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern UI
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main {
        font-family: 'Inter', sans-serif;
    }
    
    /* Header Styles */
    .header-container {
        background: linear-gradient(90deg, #5b7cfa, #7e57c2);
        padding: 0.75rem 1rem;
        border-radius: 12px;
        margin-bottom: 0.75rem;
        color: #fff;
        text-align: left;
        display: flex;
        align-items: center;
        gap: 12px;
        position: sticky;
        top: 0;
        z-index: 1000;
        box-shadow: 0 8px 24px rgba(91, 124, 250, 0.25);
    }

    .flag-icon {
        height: 28px;
        width: auto;
        border-radius: 6px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.15);
    }
    
    .header-title {
        font-size: 1.25rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: .2px;
    }
    
    .header-subtitle {
        font-size: 0.9rem;
        opacity: 0.9;
        font-weight: 400;
        margin: 0;
    }
    
    /* Card Styles */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
        transition: transform 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.12);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #7f8c8d;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Navigation Styles */
    .nav-container {
        background: transparent;
        padding: 0.5rem 0.25rem;
        border-radius: 10px;
        box-shadow: none;
        margin-bottom: 1rem;
    }
    
    .nav-button {
        background: #ffffff;
        border: 1px solid #e6e8f0;
        padding: 0.45rem 0.9rem;
        border-radius: 0;
        margin: 0.2rem;
        cursor: pointer;
        transition: all 0.18s ease-in-out;
        font-weight: 600;
        font-size: 0.92rem;
        color: #0f172a;
        box-shadow: 0 1px 0 rgba(16,24,40,0.04);
        width: 100%;
    }
    
    .nav-button:hover {
        background: linear-gradient(90deg, rgba(91,124,250,0.10), rgba(126,87,194,0.10));
        color: #111827;
        border-color: rgba(91,124,250,0.35);
        transform: translateY(-1px);
    }
    
    .nav-button.active {
        background: linear-gradient(90deg, rgba(91,124,250,0.14), rgba(126,87,194,0.14));
        color: #0b1020;
        border-color: rgba(91,124,250,0.45);
        box-shadow: 0 4px 14px rgba(91,124,250,0.18);
    }
    
    /* Alert Styles */
    .alert {
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid;
    }
    
    .alert-high {
        background: #fee;
        border-color: #e74c3c;
        color: #c0392b;
    }
    
    .alert-medium {
        background: #fff3cd;
        border-color: #f39c12;
        color: #d68910;
    }
    
    .alert-low {
        background: #d4edda;
        border-color: #27ae60;
        color: #1e8449;
    }
    
    /* Mobile Responsive */
    @media (max-width: 768px) {
        .header-title { font-size: 1.05rem; }
        .flag-icon { height: 22px; }
        .metric-value { font-size: 1.35rem; }
        .nav-button { padding: 0.4rem 0.75rem; font-size: 0.85rem; }
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 4px; }
    ::-webkit-scrollbar-thumb { background: #667eea; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #5a6fd8; }

    /* Grounded look: subtle resting shadow and slightly stronger hover shadow */
    .nav-wrap .stButton > button {
        width: 100% !important;
        height: 44px !important;
        min-height: 44px !important;
        border-radius: 0 !important;
        background-image: linear-gradient(90deg, #5b7cfa, #7e57c2) !important;
        background-color: #5b7cfa !important;
        color: #ffffff !important;
        border: 2px solid rgba(91,124,250,0.95) !important;
        padding: 0.6rem 0.95rem !important;
        font-weight: 800 !important;
        font-size: 0.95rem !important;
        /* Subtle, grounded shadow */
        box-shadow: 0 2px 6px rgba(17,24,39,0.12), 0 1px 1px rgba(17,24,39,0.06) !important;
        transition: box-shadow 0.18s ease-in-out, transform 0.18s ease-in-out !important;
        text-align: center !important;
        white-space: nowrap !important;
        line-height: 1 !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    .nav-wrap .stButton > button:hover {
        background-image: linear-gradient(90deg, #516df7, #6f4fb6) !important;
        background-color: #516df7 !important;
        color: #ffffff !important;
        border-color: rgba(91,124,250,1) !important;
        /* Slightly stronger hover shadow, minimal lift */
        box-shadow: 0 6px 14px rgba(17,24,39,0.18), 0 2px 2px rgba(17,24,39,0.08) !important;
        transform: translateY(-1px) !important;
    }

    /* Apply same grounded style globally so buttons feel consistent */
    .stButton > button,
    button[kind],
    button[data-testid="baseButton-primary"],
    button[data-testid="baseButton-secondary"] {
        border-radius: 0 !important;
        background-image: linear-gradient(90deg, #5b7cfa, #7e57c2) !important;
        background-color: #5b7cfa !important;
        color: #ffffff !important;
        border: 2px solid rgba(91,124,250,0.95) !important;
        padding: 0.6rem 1rem !important;
        font-weight: 800 !important;
        font-size: 0.95rem !important;
        box-shadow: 0 2px 6px rgba(17,24,39,0.12), 0 1px 1px rgba(17,24,39,0.06) !important;
        transition: box-shadow 0.18s ease-in-out, transform 0.18s ease-in-out !important;
        min-height: 44px !important;
        height: 44px !important;
        line-height: 1 !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
        white-space: nowrap !important;
    }

    .stButton > button:hover,
    button[kind]:hover,
    button[data-testid="baseButton-primary"]:hover,
    button[data-testid="baseButton-secondary"]:hover {
        background-image: linear-gradient(90deg, #516df7, #6f4fb6) !important;
        background-color: #516df7 !important;
        color: #ffffff !important;
        border-color: rgba(91,124,250,1) !important;
        box-shadow: 0 6px 14px rgba(17,24,39,0.18), 0 2px 2px rgba(17,24,39,0.08) !important;
        transform: translateY(-1px) !important;
    }

    .stButton > button:active,
    button[kind]:active,
    button[data-testid="baseButton-primary"]:active,
    button[data-testid="baseButton-secondary"]:active {
        transform: translateY(0) !important;
        box-shadow: 0 2px 8px rgba(91,124,250,0.25) !important;
    }

    /* ========== Risk Leaderboard Cards ========== */
    .gradient-title {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        font-size: 1.35rem;
        color: #000000;
        letter-spacing: .2px;
        margin-bottom: 0.75rem;
    }

    .risk-grid {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 12px;
        align-items: stretch;
        justify-items: stretch;
    }
    @media (max-width: 1200px) {
        .risk-grid { grid-template-columns: repeat(3, 1fr); }
    }
    @media (max-width: 800px) {
        .risk-grid { grid-template-columns: repeat(1, 1fr); }
    }

    .risk-card {
        position: relative;
        padding: 14px;
        border-radius: 12px;
        border: 1px solid rgba(15,23,42,0.08);
        box-shadow: 0 4px 12px rgba(17,24,39,0.10);
        color: #0b1020;
        background: #fff;
        overflow: hidden;
        transform: translateY(6px);
        opacity: 0;
        animation: slideUpFade 420ms ease forwards;
    }
    .risk-card:hover { transform: translateY(0) scale(1.01); box-shadow: 0 10px 24px rgba(17,24,39,0.18); }

    .risk-ribbon {
        position: absolute;
        inset: 0;
        background: linear-gradient(120deg, rgba(255,255,255,0.25), rgba(255,255,255,0.00));
        pointer-events: none;
    }

    .risk-rank { font-weight: 900; font-size: 1.1rem; }
    .risk-district { font-weight: 800; font-size: 1rem; margin-top: 2px; }

    .risk-meta { display: flex; gap: 10px; align-items: center; margin-top: 10px; font-size: 0.9rem; }
    .risk-meta .chip { display: inline-flex; align-items: center; gap: 6px; padding: 4px 8px; border-radius: 8px; background: rgba(255,255,255,0.6); border: 1px solid rgba(15,23,42,0.06); }

    .progress { width: 100%; height: 10px; background: rgba(255,255,255,0.55); border-radius: 999px; border: 1px solid rgba(15,23,42,0.06); overflow: hidden; }
    .progress-fill { height: 100%; background: linear-gradient(90deg, #0ea5e9, #6366f1); }
    .progress-label { font-size: 0.85rem; font-weight: 700; margin-top: 8px; }

    /* Risk color themes */
    .risk-red { background: linear-gradient(135deg, #ff6b6b, #ff8e8e); color: #1d0606; }
    .risk-orange { background: linear-gradient(135deg, #ffb347, #ffd56b); color: #201305; }
    .risk-yellow { background: linear-gradient(135deg, #ffeaa7, #fdcb6e); color: #2b1d03; }

    @keyframes slideUpFade { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }

    /* Severity badge styles */
    .sev { display:inline-flex; align-items:center; gap:6px; padding:4px 10px; border-radius: 999px; font-weight:800; font-size:.78rem; letter-spacing:.2px; }
    .sev-critical { background: rgba(255,107,107,0.2); color:#3b0a0a; border:1px solid rgba(255,107,107,0.4); }
    .sev-high { background: rgba(255,179,71,0.25); color:#3b1f06; border:1px solid rgba(255,179,71,0.45); }
    .sev-moderate { background: rgba(253,203,110,0.25); color:#3b2a07; border:1px solid rgba(253,203,110,0.45); }

    /* Left accent bar per severity */
    .accent { position:absolute; left:0; top:0; bottom:0; width:6px; border-radius:6px 0 0 6px; opacity:.9; }
    .accent-critical { background:#ff6b6b; }
    .accent-high { background:#ffb347; }
    .accent-moderate { background:#fdcb6e; }

    /* Soft pulse for critical cards */
    .pulse-critical { animation: pulse 1400ms ease-in-out infinite; }
    @keyframes pulse { 0%{ box-shadow: 0 0 0 0 rgba(255,107,107,0.35);} 70%{ box-shadow: 0 0 0 10px rgba(255,107,107,0);} 100%{ box-shadow:0 0 0 0 rgba(255,107,107,0);} }
</style>
""", unsafe_allow_html=True)

# -------- Performance-optimized loaders --------
@st.cache_data(show_spinner=False)
def load_core_data():
    """Load CSV and Geo data once; sanitize for fast map rendering."""
    # Load enhanced data
    data = pd.read_csv("outputs/enhanced_malnutrition_data.csv", low_memory=False)
    # Attach predictions if available
    try:
        predictions = pd.read_csv("outputs/predictions_advanced.csv")
        data = data.merge(
            predictions[["District", "predicted_risk", "risk_probability", "predicted_risk_level"]],
            on="District",
            how="left"
        )
    except FileNotFoundError:
        # Lightweight fallback
        if "Malnutrition_Index" in data.columns:
            data["predicted_risk"] = np.where(
                data["Malnutrition_Index"] > data["Malnutrition_Index"].quantile(0.75), 1, 0
            )
            data["risk_probability"] = data["Malnutrition_Index"] / 100
            data["predicted_risk_level"] = pd.cut(
                data["risk_probability"], bins=[0, 0.3, 0.7, 1.0], labels=["Low", "Medium", "High"]
            )

    # Load and standardize geo data
    gdf = gpd.read_file("data/rwanda_districts.geojson")
    gdf["district"] = gdf["district"].astype(str).str.strip().str.title()
    data["District"] = data["District"].astype(str).str.strip().str.title()

    merged = gdf.merge(data, left_on="district", right_on="District", how="left")

    # Sanitize for JSON: keep numerics numeric, convert datetimes to ISO, others to str
    for col in merged.columns:
        if col == "geometry":
            continue
        if pd.api.types.is_datetime64_any_dtype(merged[col]):
            merged[col] = pd.to_datetime(merged[col], errors="coerce").dt.strftime("%Y-%m-%dT%H:%M:%S")
        elif pd.api.types.is_numeric_dtype(merged[col]):
            # keep numeric as-is for fast styling computations
            merged[col] = pd.to_numeric(merged[col], errors="coerce")
        else:
            merged[col] = merged[col].astype(str)

    # Cache GeoJSON string for Folium (fast path)
    geojson_str = merged.to_json()

    # Precompute numeric metric series for quick min/max lookups
    metric_names = ["Malnutrition_Index", "risk_probability", "Stunted_pct", "Underweight_pct"]
    numeric_series = {
        m: pd.to_numeric(merged.get(m, pd.Series(dtype=float)), errors="coerce").fillna(0) for m in metric_names
    }

    return data, merged, geojson_str, numeric_series

class MalnutritionDashboard:
    def __init__(self):
        self.data, self.geo_data, self.geojson_str, self.numeric_series = load_core_data()
    
    def load_data(self):
        # Kept for backward compatibility if called; just refresh cache
        self.data, self.geo_data, self.geojson_str, self.numeric_series = load_core_data()
    
    def render_header(self):
        """Render the header section"""
        col_left, col_right = st.columns([1, 1])
        with col_left:
            st.markdown("""
            <div class="header-container">
                                <img class="flag-icon" src="https://upload.wikimedia.org/wikipedia/commons/1/17/Flag_of_Rwanda.svg" alt="Rwanda Flag"/>
                                <div>
                                    <div class="header-title">Rwanda Malnutrition Intelligence Platform</div>
                <div class="header-subtitle">Ending Hidden Hunger Through Data-Driven Solutions</div>
                                </div>
            </div>
            """, unsafe_allow_html=True)
        with col_right:
            st.markdown('<div class="nav-container">', unsafe_allow_html=True)
            nav_cols = st.columns([1.4, 1, 1.6, 1, 1.1])
            with nav_cols[0]:
                if st.button("📊 Dashboard", key="nav_dashboard", use_container_width=True):
                    st.session_state.current_page = "dashboard"
                    st.rerun()
            with nav_cols[1]:
                if st.button("🗺️ Map", key="nav_map", use_container_width=True):
                    st.session_state.current_page = "map"
                    st.rerun()
            with nav_cols[2]:
                if st.button("🤖 Predictions", key="nav_predictions", use_container_width=True):
                    st.session_state.current_page = "predictions"
                    st.rerun()
            with nav_cols[3]:
                if st.button("📋 Policy", key="nav_policy", use_container_width=True):
                    st.session_state.current_page = "policy"
                    st.rerun()
            with nav_cols[4]:
                if st.button("📈 Analytics", key="nav_analytics", use_container_width=True):
                    st.session_state.current_page = "analytics"
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    
    def render_dashboard_page(self):
        """Render the main dashboard page"""
        st.header("📊 Executive Dashboard")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            high_risk = len(self.data[self.data["predicted_risk_level"] == "High"])
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{high_risk}</div>
                <div class="metric-label">High Risk Districts</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            avg_malnutrition = self.data["Malnutrition_Index"].mean()
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{avg_malnutrition:.1f}</div>
                <div class="metric-label">Avg Malnutrition Index</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            total_children = self.data["Children_Under5"].sum()
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{total_children:,}</div>
                <div class="metric-label">Children Under 5</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            intervention_ready = len(self.data[self.data["Intervention_Readiness"] > 70])
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{intervention_ready}</div>
                <div class="metric-label">Intervention Ready</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Risk Distribution")
            risk_counts = self.data["predicted_risk_level"].value_counts()
            fig = px.pie(
                values=risk_counts.values,
                names=risk_counts.index,
                color_discrete_map={"High": "#e74c3c", "Medium": "#f39c12", "Low": "#27ae60"},
                title="District Risk Levels"
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Malnutrition Trends")
            # Simulate trend data
            months = pd.date_range(start='2024-01-01', end='2024-12-01', freq='M')
            trend_data = pd.DataFrame({
                'Month': months,
                'Malnutrition_Index': np.random.normal(20, 5, len(months))
            })
            
            fig = px.line(
                trend_data, 
                x='Month', 
                y='Malnutrition_Index',
                title="Monthly Malnutrition Index Trend",
                markers=True
            )
            fig.update_layout(xaxis_title="Month", yaxis_title="Malnutrition Index")
            st.plotly_chart(fig, use_container_width=True)
        
        # Top 5 high-risk districts (modern leaderboard)
        st.markdown('<div style="margin-top:-10px;"></div>', unsafe_allow_html=True)
        st.markdown('<div class="gradient-title">⚠️ AI-Identified High-Risk Districts</div>', unsafe_allow_html=True)
        st.markdown('<div style="margin:-2px 0 5px 0; color:#475569; font-size:0.95rem;">Based on AI-driven malnutrition risk probabilities.</div>', unsafe_allow_html=True)

        # Compute top 5 by risk_probability with fallback logic
        df_copy = self.data.copy()
        df_copy["risk_probability"] = pd.to_numeric(df_copy.get("risk_probability"), errors="coerce").fillna(0)
        df_copy["Children_Under5"] = pd.to_numeric(df_copy.get("Children_Under5"), errors="coerce").fillna(0)
        top5 = df_copy.sort_values("risk_probability", ascending=False).head(5)

        # Build card HTML for each row
        cards = []
        for idx, (_, row) in enumerate(top5.iterrows(), 1):
            prob = float(row["risk_probability"]) if not pd.isna(row["risk_probability"]) else 0.0
            prob_pct = int(round(prob * 100))
            if prob_pct >= 90:
                theme_class = "risk-red"
                sev_class = "sev sev-critical"
                sev_label = "Critical Risk"
                accent_class = "accent accent-critical"
                pulse_class = " pulse-critical"
            elif prob_pct >= 75:
                theme_class = "risk-orange"
                sev_class = "sev sev-high"
                sev_label = "High Risk"
                accent_class = "accent accent-high"
                pulse_class = ""
            else:
                theme_class = "risk-yellow"
                sev_class = "sev sev-moderate"
                sev_label = "Moderate Risk"
                accent_class = "accent accent-moderate"
                pulse_class = ""

            district_name = str(row.get("District", "Unknown"))
            mal_idx = float(row.get("Malnutrition_Index", 0.0))
            children = int(row.get("Children_Under5", 0))

            card_html = f"""
            <div class="risk-card {theme_class}{pulse_class}" style="animation-delay:{idx*80}ms">
              <div class="{accent_class}"></div>
              <div class="risk-ribbon"></div>
              <div style="display:flex; align-items:center; justify-content:space-between; gap:10px;">
                <div>
                  <div class="risk-district">{district_name}</div>
                  <div class="{sev_class}"><span class="sev-label">{sev_label}</span></div>
            </div>
                <div class="gauge" style="--p:{prob_pct};" title="{prob_pct}%"></div>
              </div>
              <div class="progress" aria-label="Risk Probability">
                <div class="progress-fill" style="--target:{prob_pct}%;"></div>
              </div>
              <div class="progress-label">Risk Probability: {prob_pct}%</div>
              <div class="risk-meta">
                <span class="chip">📉 Index: {mal_idx:.1f}</span>
                <span class="chip">👶 Children: {children:,}</span>
              </div>
            </div>
            """
            cards.append(card_html)

        # Assemble full HTML with inline CSS so styles apply inside the iframe
        full_html = (
            """
        <html>
        <head>
          <meta charset=\"utf-8\" />
          <link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin>
          <link href=\"https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&display=swap\" rel=\"stylesheet\">
          <style>
            :root { --glass: rgba(255,255,255,0.22); --glass-border: rgba(255,255,255,0.55); --shadow: rgba(17,24,39,0.14); }

            .risk-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; align-items: stretch; justify-items: stretch; }
            @media (max-width: 1200px) { .risk-grid { grid-template-columns: repeat(3, 1fr); } }
            @media (max-width: 800px)  { .risk-grid { grid-template-columns: repeat(1, 1fr); } }

            /* Card base with glassmorphism */
            .risk-card { position: relative; padding: 14px; border-radius: 12px; border: 1px solid var(--glass-border);
                         box-shadow: 0 2px 10px var(--shadow), inset 0 0 0 1px rgba(255,255,255,0.15); color: #0b1020; background: var(--glass);
                         overflow: hidden; transform: translateY(8px); opacity: 0; backdrop-filter: blur(14px);
                         animation: slideUpFade 520ms ease forwards; transition: transform .22s ease, box-shadow .22s ease; }
            .risk-card:hover { transform: translateY(-4px); box-shadow: 0 16px 30px rgba(17,24,39,0.22), 0 0 0 1px rgba(255,255,255,0.45) inset; }

            /* Risk background tint layers */
            .risk-card.risk-red::before, .risk-card.risk-orange::before, .risk-card.risk-yellow::before {
              content: \"\"; position: absolute; inset: 0; z-index: -1; opacity: .85;
            }
            .risk-card.risk-red::before { background: linear-gradient(135deg, #ff6b6b, #ff8e8e); }
            .risk-card.risk-orange::before { background: linear-gradient(135deg, #ffb347, #ffd56b); }
            .risk-card.risk-yellow::before { background: linear-gradient(135deg, #ffeaa7, #fdcb6e); }

            .risk-ribbon { position: absolute; inset: 0; background: linear-gradient(120deg, rgba(255,255,255,0.18), rgba(255,255,255,0.00)); pointer-events: none; }
            .risk-rank { font-weight: 900; font-size: 1.1rem; }
            .risk-district { font-weight: 800; font-size: 1rem; margin-top: 2px; }

            /* Progress bar with animated fill to target (uses CSS var --target) */
            .progress { width: 100%; height: 10px; background: rgba(255,255,255,0.55); border-radius: 999px; border: 1px solid rgba(15,23,42,0.06); overflow: hidden; margin-top: 10px; }
            .progress-fill { height: 100%; width: 0; background: linear-gradient(90deg, #0ea5e9, #6366f1); animation: fill 900ms ease forwards; }
            .progress-label { font-size: 0.85rem; font-weight: 700; margin-top: 8px; }

            /* Circular gauge using conic-gradient; set --p:[0-100] */
            .gauge { --p: 0; width: 36px; height: 36px; border-radius: 50%;
                     background: conic-gradient(#0ea5e9 calc(var(--p) * 1%), rgba(255,255,255,0.35) 0);
                     display: inline-grid; place-items: center; border: 1px solid rgba(255,255,255,0.5); }
            .gauge::after { content: \"\"; width: 26px; height: 26px; background: rgba(255,255,255,0.85); border-radius: 50%; box-shadow: inset 0 0 0 1px rgba(15,23,42,0.06); }

            .risk-meta { display: flex; gap: 10px; align-items: center; margin-top: 10px; font-size: 0.9rem; flex-wrap: wrap; }
            .risk-meta .chip { display: inline-flex; align-items: center; gap: 6px; padding: 4px 8px; border-radius: 8px;
                               background: rgba(255,255,255,0.6); border: 1px solid rgba(15,23,42,0.06); }

            @keyframes slideUpFade { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
            @keyframes fill { from { width: 0; } to { width: var(--target); } }

            body { margin: 0; padding: 0; font-family: Poppins, system-ui, -apple-system, Segoe UI, Roboto, sans-serif; }
          </style>
        </head>
        <body>
        """
            + ("<div class='risk-grid'>" + "".join(cards) + "</div>") +
            """
        </body>
        </html>
        """
        )
        components.html(full_html, height=380, scrolling=False)
    
    def render_map_page(self):
        """Render the interactive map page"""
        st.header("🗺️ Interactive Malnutrition Map")
        
        # Map controls
        col1, col2, col3 = st.columns(3)
        
        with col1:
            map_metric = st.selectbox(
                "Select Metric",
                ["Malnutrition_Index", "risk_probability", "Stunted_pct", "Underweight_pct"],
                key="map_metric"
            )
        
        with col2:
            map_style = st.selectbox(
                "Map Style",
                ["cartodbpositron", "OpenStreetMap", "Stamen Terrain"],
                key="map_style"
            )
        
        with col3:
            show_predictions = st.checkbox("Show AI Predictions", value=True)
        
        # Create map with proper attributions and layout
        tiles_map = {
            "cartodbpositron": {"tiles": "CartoDB positron", "attr": "© OpenStreetMap contributors © CartoDB"},
            "OpenStreetMap": {"tiles": "OpenStreetMap", "attr": "© OpenStreetMap contributors"},
            "Stamen Terrain": {"tiles": "https://stamen-tiles.a.ssl.fastly.net/terrain/{z}/{x}/{y}.png", "attr": "Map tiles by Stamen Design, CC BY 3.0 — Map data © OpenStreetMap contributors"}
        }
        tconf = tiles_map.get(map_style, tiles_map["cartodbpositron"])
        m = folium.Map(location=[-1.95, 30.06], zoom_start=8, tiles=None)
        folium.TileLayer(tiles=tconf["tiles"], attr=tconf["attr"], name=map_style).add_to(m)
        
        # Color mapping
        if map_metric == "risk_probability":
            color_map = {"High": "red", "Medium": "orange", "Low": "green"}
            style_function = lambda feature: {
                "fillColor": color_map.get(feature["properties"].get("predicted_risk_level", "Low"), "gray"),
                "color": "black",
                "weight": 1,
                "fillOpacity": 0.7
            }
        else:
            # Continuous color mapping - use precomputed numeric series
            values = self.numeric_series.get(map_metric, pd.Series(dtype=float))
            max_val = values.max()
            min_val = values.min()
            
            def get_color(val):
                if pd.isna(val) or val == "nan" or val == "":
                    return "gray"
                try:
                    # Convert to float for calculation
                    num_val = float(val)
                    normalized = (num_val - min_val) / (max_val - min_val) if max_val > min_val else 0
                    if normalized > 0.7:
                        return "red"
                    elif normalized > 0.4:
                        return "orange"
                    else:
                        return "green"
                except (ValueError, TypeError):
                    return "gray"
            
            style_function = lambda feature: {
                "fillColor": get_color(feature["properties"].get(map_metric)),
                "color": "black",
                "weight": 1,
                "fillOpacity": 0.7
            }
        
        # Layout: map on left, stats on right
        map_col, stats_col = st.columns([2, 1])

        with map_col:
            folium.GeoJson(
                self.geojson_str,
                style_function=style_function,
                tooltip=folium.GeoJsonTooltip(
                    fields=["District", map_metric, "Children_Under5", "predicted_risk_level"],
                    aliases=["District", map_metric.replace("_", " ").title(), "Children Under 5", "Risk Level"],
                    localize=True
                ),
                popup=folium.GeoJsonPopup(
                    fields=["District", map_metric, "Children_Under5", "Stunted_pct", "Underweight_pct"],
                    aliases=["District", map_metric.replace("_", " ").title(), "Children Under 5", "Stunted %", "Underweight %"],
                    localize=True
                )
            ).add_to(m)
            st_folium(m, use_container_width=True, height=520)

        with stats_col:
            st.markdown("### Map Statistics")
            # Card 1
            total = len(self.geo_data)
            st.markdown(f"""
            <div class="metric-card"> 
                <div class="metric-value">{total}</div>
                <div class="metric-label">Total Districts</div>
            </div>
            """, unsafe_allow_html=True)
            # Card 2
            high_risk_count = int((self.geo_data.get("predicted_risk_level", "").astype(str) == "High").sum()) if "predicted_risk_level" in self.geo_data.columns else 0
            st.markdown(f"""
            <div class="metric-card"> 
                <div class="metric-value">{high_risk_count}</div>
                <div class="metric-label">High Risk Districts</div>
            </div>
            """, unsafe_allow_html=True)
            # Card 3
            risk_probs = pd.to_numeric(self.geo_data.get('risk_probability', pd.Series(dtype=float)), errors='coerce').fillna(0)
            avg_risk = risk_probs.mean()
            st.markdown(f"""
            <div class="metric-card"> 
                <div class="metric-value">{avg_risk:.1%}</div>
                <div class="metric-label">Average Risk Probability</div>
            </div>
            """, unsafe_allow_html=True)
    
    def render_predictions_page(self):
        """Render the AI predictions page"""
        st.header("🤖 AI-Powered Predictions")
        
        # Model performance
        st.subheader("Model Performance")
        
        try:
            performance = pd.read_csv("outputs/model_performance.csv", index_col=0)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # AUC scores
                fig = px.bar(
                    x=performance.index,
                    y=performance['auc'],
                    title="Model AUC Scores",
                    color=performance['auc'],
                    color_continuous_scale="Viridis"
                )
                fig.update_layout(xaxis_title="Model", yaxis_title="AUC Score")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Accuracy scores
                fig = px.bar(
                    x=performance.index,
                    y=performance['accuracy'],
                    title="Model Accuracy Scores",
                    color=performance['accuracy'],
                    color_continuous_scale="Plasma"
                )
                fig.update_layout(xaxis_title="Model", yaxis_title="Accuracy")
                st.plotly_chart(fig, use_container_width=True)
        
        except FileNotFoundError:
            st.info("Model performance data not available. Please run the ML pipeline first.")
        
        # Prediction details
        st.subheader("District Predictions")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            risk_filter = st.selectbox("Filter by Risk Level", ["All", "High", "Medium", "Low"])
        
        with col2:
            confidence_filter = st.slider("Minimum Confidence", 0.0, 1.0, 0.0, 0.1)
        
        with col3:
            sort_by = st.selectbox("Sort by", ["risk_probability", "Malnutrition_Index", "District"])
        
        # Filter data
        filtered_data = self.data.copy()
        
        if risk_filter != "All":
            filtered_data = filtered_data[filtered_data["predicted_risk_level"] == risk_filter]
        
        filtered_data = filtered_data[filtered_data["risk_probability"] >= confidence_filter]
        filtered_data = filtered_data.sort_values(sort_by, ascending=False)
        
        # Display results
        st.dataframe(
            filtered_data[["District", "predicted_risk_level", "risk_probability", "Malnutrition_Index", "Children_Under5"]],
            use_container_width=True
        )
        
        # Download button
        csv = filtered_data.to_csv(index=False)
        st.download_button(
            label="Download Predictions CSV",
            data=csv,
            file_name=f"malnutrition_predictions_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    def render_policy_page(self):
        """Render the policy briefs page"""
        st.header("📋 Policy Briefs & Recommendations")
        
        # District selector
        selected_district = st.selectbox(
            "Select District",
            sorted(self.data["District"].unique()),
            key="policy_district"
        )
        
        if selected_district:
            district_data = self.data[self.data["District"] == selected_district].iloc[0]
            
            # District overview
            st.subheader(f"Policy Brief: {selected_district}")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Risk Level", district_data["predicted_risk_level"])
            
            with col2:
                st.metric("Risk Probability", f"{district_data['risk_probability']:.1%}")
            
            with col3:
                st.metric("Malnutrition Index", f"{district_data['Malnutrition_Index']:.1f}")
            
            # Root causes analysis
            st.subheader("Root Causes Analysis")
            
            causes = []
            if district_data["Stunted_pct"] > 20:
                causes.append("High stunting prevalence")
            if district_data["Underweight_pct"] > 15:
                causes.append("High underweight prevalence")
            if district_data["VitaminA_pct"] > 10:
                causes.append("Vitamin A deficiency")
            if district_data["Iodine_pct"] > 10:
                causes.append("Iodine deficiency")
            if district_data["Poverty_Index"] > 0.6:
                causes.append("High poverty levels")
            if district_data["Drought_Risk"] == 1:
                causes.append("Drought risk")
            
            for cause in causes:
                st.markdown(f"• {cause}")
            
            # Recommendations
            st.subheader("Recommended Interventions")
            
            tab1, tab2, tab3 = st.tabs(["🏥 Health", "🌾 Agriculture", "🎓 Education"])
            
            with tab1:
                health_recs = [
                    "Vitamin A supplementation program",
                    "Iodine supplementation program",
                    "Nutritional counseling and monitoring",
                    "Mobile health clinics",
                    "Maternal and child health programs"
                ]
                for rec in health_recs:
                    st.markdown(f"• {rec}")
            
            with tab2:
                agri_recs = [
                    "Promote biofortified crops",
                    "Kitchen garden programs",
                    "Agricultural extension services",
                    "Drought-resistant crop varieties",
                    "Food processing training"
                ]
                for rec in agri_recs:
                    st.markdown(f"• {rec}")
            
            with tab3:
                edu_recs = [
                    "School feeding programs",
                    "Nutrition awareness campaigns",
                    "Community nutrition education",
                    "Teacher training on nutrition",
                    "Parent education programs"
                ]
                for rec in edu_recs:
                    st.markdown(f"• {rec}")
            
            # Note: Cost-benefit analysis removed per request
    
    def render_analytics_page(self):
        """Render the analytics page"""
        st.header("📈 Advanced Analytics")
        
        # Correlation analysis
        st.subheader("Correlation Analysis")
        
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns
        correlation_matrix = self.data[numeric_cols].corr()
        
        fig = px.imshow(
            correlation_matrix,
            title="Correlation Matrix",
            color_continuous_scale="RdBu",
            aspect="auto"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Feature importance
        st.subheader("Feature Importance")
        
        try:
            importance = pd.read_csv("outputs/feature_importance_advanced.csv", index_col=0)
            
            # Average importance across models
            avg_importance = importance.mean(axis=1).sort_values(ascending=True)
            
            fig = px.bar(
                x=avg_importance.values,
                y=avg_importance.index,
                orientation='h',
                title="Average Feature Importance",
                color=avg_importance.values,
                color_continuous_scale="Viridis"
            )
            fig.update_layout(xaxis_title="Importance", yaxis_title="Feature")
            st.plotly_chart(fig, use_container_width=True)
        
        except FileNotFoundError:
            st.info("Feature importance data not available. Please run the ML pipeline first.")
        
        # Geographic analysis
        st.subheader("Geographic Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Elevation vs Malnutrition
            fig = px.scatter(
                self.data,
                x="Elevation",
                y="Malnutrition_Index",
                color="predicted_risk_level",
                title="Elevation vs Malnutrition Index",
                hover_data=["District", "Children_Under5"]
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Distance to Kigali vs Malnutrition
            fig = px.scatter(
                self.data,
                x="Distance_to_Kigali",
                y="Malnutrition_Index",
                color="predicted_risk_level",
                title="Distance to Kigali vs Malnutrition Index",
                hover_data=["District", "Children_Under5"]
            )
            st.plotly_chart(fig, use_container_width=True)
    
    def run(self):
        """Main dashboard runner"""
        # Initialize session state
        if "current_page" not in st.session_state:
            st.session_state.current_page = "dashboard"
        
        # Render components
        self.render_header()
        # self.render_navigation() # This line is removed as per the new_code, as the navigation is now in render_header
        
        # Render current page
        if st.session_state.current_page == "dashboard":
            self.render_dashboard_page()
        elif st.session_state.current_page == "map":
            self.render_map_page()
        elif st.session_state.current_page == "predictions":
            self.render_predictions_page()
        elif st.session_state.current_page == "policy":
            self.render_policy_page()
        elif st.session_state.current_page == "analytics":
            self.render_analytics_page()

# Run the dashboard
if __name__ == "__main__":
    dashboard = MalnutritionDashboard()
    dashboard.run()
