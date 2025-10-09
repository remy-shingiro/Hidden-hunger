# fixed_realtime_integration.py
# Fixed real-time integration without infinite loading

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import time

# Page configuration
st.set_page_config(
    page_title="Real-time Malnutrition Monitor",
    page_icon="🔄",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .metric-container {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    
    .alert-box {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-online {
        background-color: #27ae60;
    }
    
    .status-offline {
        background-color: #e74c3c;
    }
</style>
""", unsafe_allow_html=True)

class RealTimeMonitor:
    def __init__(self):
        self.data = None
        self.load_data()
    
    @st.cache_data(show_spinner=False)
    def _load_data_cached(_ts: int):
        df = None
        try:
            df = pd.read_csv("outputs/enhanced_malnutrition_data.csv", low_memory=False)
        except FileNotFoundError:
            df = pd.read_csv("data/malnutrition_sample.csv", low_memory=False)
        if "District" in df.columns:
            df["District"] = df["District"].astype(str).str.strip().str.title()
        return df

    def load_data(self):
        """Load data with fallback (cached)"""
        self.data = self._load_data_cached(int(datetime.now().strftime("%Y%m%d")))
    
    def generate_live_metrics(self):
        """Generate simulated live metrics"""
        # Simulate real-time data
        current_time = datetime.now()
        
        # Generate random variations for live feel
        base_malnutrition = (
            pd.to_numeric(self.data.get("Malnutrition_Index", pd.Series(dtype=float)), errors="coerce")
            .fillna(0)
            .mean()
        )
        live_malnutrition = base_malnutrition + np.random.normal(0, 2)
        
        base_stunting = (
            pd.to_numeric(self.data.get("Stunted_pct", pd.Series(dtype=float)), errors="coerce")
            .fillna(0)
            .mean()
        )
        live_stunting = base_stunting + np.random.normal(0, 1)
        
        # Weather simulation
        temperature = 22 + np.random.normal(0, 2)
        rainfall = max(0, 5 + np.random.normal(0, 3))
        
        # Robust high risk computation
        if "predicted_risk_level" in self.data.columns:
            mask_high = self.data["predicted_risk_level"].astype(str) == "High"
        else:
            # Fallback: use Malnutrition_Index percentile threshold
            mal_idx_series = pd.to_numeric(self.data.get("Malnutrition_Index", pd.Series(dtype=float)), errors="coerce").fillna(0)
            if len(mal_idx_series) > 0:
                threshold = mal_idx_series.quantile(0.75)
            else:
                threshold = 0
            mask_high = mal_idx_series >= threshold
        high_risk_count = int(mask_high.sum())

        # Robust total children
        total_children_series = pd.to_numeric(self.data.get("Children_Under5", pd.Series(dtype=float)), errors="coerce").fillna(0)
        total_children_val = int(total_children_series.sum()) if len(total_children_series) else 0

        return {
            "timestamp": current_time,
            "malnutrition_index": live_malnutrition,
            "stunting_rate": live_stunting,
            "temperature": temperature,
            "rainfall": rainfall,
            "high_risk_districts": high_risk_count,
            "total_children": total_children_val,
            "system_status": "online"
        }
    
    def render_header(self):
        """Render header section"""
        st.markdown("""
        <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 15px; margin-bottom: 2rem;">
            <h1 style="margin: 0; font-size: 2.5rem;">🔄 Real-time Malnutrition Monitor</h1>
            <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Live monitoring of malnutrition indicators across Rwanda</p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_live_metrics(self):
        """Render live metrics dashboard"""
        st.header("📊 Live Metrics")
        
        # Generate live data
        metrics = self.generate_live_metrics()
        
        # Display metrics in columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-container">
                <h3 style="margin: 0; color: #2c3e50;">{metrics['malnutrition_index']:.1f}</h3>
                <p style="margin: 0; color: #7f8c8d;">Malnutrition Index</p>
                <small style="color: #95a5a6;">Last updated: {metrics['timestamp'].strftime('%H:%M:%S')}</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-container">
                <h3 style="margin: 0; color: #2c3e50;">{metrics['stunting_rate']:.1f}%</h3>
                <p style="margin: 0; color: #7f8c8d;">Stunting Rate</p>
                <small style="color: #95a5a6;">Live data</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-container">
                <h3 style="margin: 0; color: #2c3e50;">{metrics['temperature']:.1f}°C</h3>
                <p style="margin: 0; color: #7f8c8d;">Temperature</p>
                <small style="color: #95a5a6;">Current</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-container">
                <h3 style="margin: 0; color: #2c3e50;">{metrics['rainfall']:.1f}mm</h3>
                <p style="margin: 0; color: #7f8c8d;">Rainfall</p>
                <small style="color: #95a5a6;">Today</small>
            </div>
            """, unsafe_allow_html=True)
        
        # System status
        st.markdown(f"""
        <div class="alert-box">
            <span class="status-indicator status-online"></span>
            <strong>System Status:</strong> Online | 
            <strong>Last Update:</strong> {metrics['timestamp'].strftime('%Y-%m-%d %H:%M:%S')} | 
            <strong>Data Sources:</strong> 4 Active
        </div>
        """, unsafe_allow_html=True)
    
    def render_alerts(self):
        """Render alerts section"""
        st.header("🚨 Active Alerts")
        
        # Generate sample alerts
        alerts = [
            {
                "type": "High Risk",
                "district": "Rubavu",
                "message": "Malnutrition index above threshold",
                "severity": "high",
                "timestamp": datetime.now() - timedelta(minutes=15)
            },
            {
                "type": "Weather Warning",
                "district": "Nyagatare",
                "message": "Drought conditions detected",
                "severity": "medium",
                "timestamp": datetime.now() - timedelta(hours=1)
            },
            {
                "type": "Supply Alert",
                "district": "Huye",
                "message": "Vitamin A supplements running low",
                "severity": "medium",
                "timestamp": datetime.now() - timedelta(hours=2)
            }
        ]
        
        for alert in alerts:
            severity_color = {"high": "#e74c3c", "medium": "#f39c12", "low": "#27ae60"}.get(alert["severity"], "#95a5a6")
            
            with st.expander(f"🚨 {alert['type']} - {alert['district']} ({alert['severity'].title()})"):
                st.write(f"**Message:** {alert['message']}")
                st.write(f"**District:** {alert['district']}")
                st.write(f"**Severity:** {alert['severity'].title()}")
                st.write(f"**Time:** {alert['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
                
                if st.button(f"Mark as Read", key=f"alert_{alert['district']}"):
                    st.success("Alert marked as read")
    
    def render_trends(self):
        """Render trends section"""
        st.header("📈 Live Trends")
        
        # Generate trend data
        hours = list(range(24))
        malnutrition_trend = [20 + np.random.normal(0, 2) for _ in hours]
        stunting_trend = [15 + np.random.normal(0, 1) for _ in hours]
        
        # Create trend chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=hours,
            y=malnutrition_trend,
            mode='lines+markers',
            name='Malnutrition Index',
            line=dict(color='#667eea', width=3),
            marker=dict(size=6)
        ))
        
        fig.add_trace(go.Scatter(
            x=hours,
            y=stunting_trend,
            mode='lines+markers',
            name='Stunting Rate (%)',
            line=dict(color='#e74c3c', width=3),
            marker=dict(size=6),
            yaxis='y2'
        ))
        
        fig.update_layout(
            title="24-Hour Live Trends",
            xaxis_title="Hours Ago",
            yaxis_title="Malnutrition Index",
            yaxis2=dict(title="Stunting Rate (%)", overlaying="y", side="right"),
            height=400,
            showlegend=True,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_district_monitor(self):
        """Render district monitoring"""
        st.header("🗺️ District Monitor")
        
        # Top 5 districts by risk
        if "predicted_risk_level" in self.data.columns:
            high_risk_districts = self.data[self.data["predicted_risk_level"] == "High"].head(5)
        else:
            # Fallback: use malnutrition index
            high_risk_districts = self.data.nlargest(5, "Malnutrition_Index")
        
        for idx, (_, district) in enumerate(high_risk_districts.iterrows(), 1):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"**{idx}. {district['District']}**")
            
            with col2:
                malnutrition_idx = district.get("Malnutrition_Index", 0)
                st.metric("Risk Index", f"{malnutrition_idx:.1f}")
            
            with col3:
                children = district.get("Children_Under5", 0)
                st.metric("Children", f"{children:,}")
    
    def render_weather_impact(self):
        """Render weather impact analysis"""
        st.header("🌤️ Weather Impact")
        
        # Simulate weather data for different districts
        districts = ["Kigali", "Huye", "Musanze", "Rubavu", "Nyagatare"]
        weather_data = []
        
        for district in districts:
            weather_data.append({
                "District": district,
                "Temperature": 22 + np.random.normal(0, 3),
                "Rainfall": max(0, 5 + np.random.normal(0, 4)),
                "Humidity": 70 + np.random.normal(0, 10),
                "Malnutrition_Risk": 20 + np.random.normal(0, 5)
            })
        
        weather_df = pd.DataFrame(weather_data)
        
        # Temperature vs Malnutrition Risk
        fig = px.scatter(
            weather_df,
            x="Temperature",
            y="Malnutrition_Risk",
            size="Rainfall",
            color="District",
            title="Temperature vs Malnutrition Risk",
            hover_data=["Humidity"]
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def run(self):
        """Main application runner"""
        self.render_header()
        
        # Auto-refresh toggle
        auto_refresh = st.checkbox("Enable Auto-Refresh (30 seconds)", value=False)
        
        if auto_refresh:
            # Auto-refresh every 30 seconds
            time.sleep(30)
            st.rerun()
        
        # Manual refresh button
        if st.button("🔄 Refresh Data"):
            st.rerun()
        
        # Main content tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Live Metrics", "🚨 Alerts", "📈 Trends", "🗺️ Districts", "🌤️ Weather"
        ])
        
        with tab1:
            self.render_live_metrics()
        
        with tab2:
            self.render_alerts()
        
        with tab3:
            self.render_trends()
        
        with tab4:
            self.render_district_monitor()
        
        with tab5:
            self.render_weather_impact()
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #7f8c8d; padding: 1rem;">
            <p>🔄 Real-time Malnutrition Monitor | 🇷🇼 Rwanda | NISR Big Data Hackathon 2025</p>
            <p>Last updated: {}</p>
        </div>
        """.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), unsafe_allow_html=True)

# Run the application
if __name__ == "__main__":
    monitor = RealTimeMonitor()
    monitor.run()
