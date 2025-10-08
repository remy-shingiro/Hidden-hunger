# mobile_app.py
# Mobile-optimized Streamlit app with offline capabilities

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import base64
from io import BytesIO

# Mobile-optimized page config
st.set_page_config(
    page_title="Rwanda Malnutrition Mobile",
    page_icon="🇷🇼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Mobile-optimized CSS
st.markdown("""
<style>
    /* Mobile-first responsive design */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem;
        }
        
        .stSelectbox, .stSlider, .stButton {
            width: 100%;
        }
        
        .metric-card {
            margin-bottom: 1rem;
            padding: 1rem;
        }
        
        .chart-container {
            height: 300px;
        }
    }
    
    /* Mobile navigation */
    .mobile-nav {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: white;
        border-top: 1px solid #e0e0e0;
        padding: 0.5rem;
        z-index: 1000;
        display: flex;
        justify-content: space-around;
    }
    
    .nav-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 0.5rem;
        text-decoration: none;
        color: #666;
        font-size: 0.8rem;
    }
    
    .nav-item.active {
        color: #667eea;
    }
    
    .nav-icon {
        font-size: 1.5rem;
        margin-bottom: 0.25rem;
    }
    
    /* Offline indicator */
    .offline-indicator {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        background: #f39c12;
        color: white;
        text-align: center;
        padding: 0.5rem;
        z-index: 1001;
    }
    
    /* Touch-friendly buttons */
    .touch-button {
        min-height: 44px;
        min-width: 44px;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        border: none;
        background: #667eea;
        color: white;
        font-size: 1rem;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .touch-button:active {
        transform: scale(0.95);
        background: #5a6fd8;
    }
    
    /* Card styles for mobile */
    .mobile-card {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    
    .mobile-card h3 {
        margin: 0 0 0.5rem 0;
        color: #2c3e50;
        font-size: 1.1rem;
    }
    
    .mobile-card p {
        margin: 0;
        color: #7f8c8d;
        font-size: 0.9rem;
    }
    
    /* Hide desktop elements on mobile */
    @media (max-width: 768px) {
        .desktop-only {
            display: none;
        }
    }
    
    /* Show mobile elements only on mobile */
    @media (min-width: 769px) {
        .mobile-only {
            display: none;
        }
    }
</style>
""", unsafe_allow_html=True)

class MobileMalnutritionApp:
    def __init__(self):
        self.data = None
        self.load_data()
        self.offline_mode = False
    
    def load_data(self):
        """Load data with offline fallback"""
        try:
            self.data = pd.read_csv("outputs/enhanced_malnutrition_data.csv")
            self.offline_mode = False
        except FileNotFoundError:
            # Fallback to basic data
            try:
                self.data = pd.read_csv("data/malnutrition_sample.csv")
                self.offline_mode = True
                st.warning("⚠️ Using offline data. Some features may be limited.")
            except FileNotFoundError:
                st.error("❌ No data available. Please ensure data files are present.")
                st.stop()
    
    def render_mobile_header(self):
        """Render mobile-optimized header"""
        st.markdown("""
        <div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px; margin-bottom: 1rem;">
            <h1 style="margin: 0; font-size: 1.5rem;">🇷🇼 Rwanda Malnutrition</h1>
            <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Mobile Intelligence Platform</p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_offline_indicator(self):
        """Render offline mode indicator"""
        if self.offline_mode:
            st.markdown("""
            <div class="offline-indicator">
                📱 Offline Mode - Limited Features Available
            </div>
            """, unsafe_allow_html=True)
    
    def render_quick_stats(self):
        """Render quick statistics cards"""
        st.subheader("📊 Quick Stats")
        
        # Calculate stats
        total_districts = len(self.data)
        high_risk = len(self.data[self.data.get("predicted_risk_level", "Low") == "High"]) if "predicted_risk_level" in self.data.columns else 0
        total_children = self.data["Children_Under5"].sum() if "Children_Under5" in self.data.columns else 0
        avg_stunted = self.data["Stunted_pct"].mean() if "Stunted_pct" in self.data.columns else 0
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class="mobile-card">
                <h3>{total_districts}</h3>
                <p>Total Districts</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="mobile-card">
                <h3>{high_risk}</h3>
                <p>High Risk Districts</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="mobile-card">
                <h3>{total_children:,}</h3>
                <p>Children Under 5</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="mobile-card">
                <h3>{avg_stunted:.1f}%</h3>
                <p>Avg Stunting Rate</p>
            </div>
            """, unsafe_allow_html=True)
    
    def render_district_selector(self):
        """Render district selector with search"""
        st.subheader("🔍 District Lookup")
        
        # Search box
        search_term = st.text_input("Search District", placeholder="Type district name...")
        
        # Filter districts
        if search_term:
            filtered_districts = self.data[
                self.data["District"].str.contains(search_term, case=False, na=False)
            ]
        else:
            filtered_districts = self.data
        
        # District list
        for idx, (_, district) in enumerate(filtered_districts.head(10).iterrows()):
            with st.expander(f"{district['District']} - Risk: {district.get('predicted_risk_level', 'Unknown')}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Children Under 5", f"{district['Children_Under5']:,}")
                    st.metric("Stunted", f"{district['Stunted']:,}")
                
                with col2:
                    st.metric("Underweight", f"{district['Underweight']:,}")
                    st.metric("Wasted", f"{district['Wasted']:,}")
                
                # Risk assessment
                if "predicted_risk_level" in district:
                    risk_color = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(district["predicted_risk_level"], "⚪")
                    st.write(f"**Risk Level:** {risk_color} {district['predicted_risk_level']}")
    
    def render_quick_assessment(self):
        """Render quick malnutrition assessment tool"""
        st.subheader("⚡ Quick Assessment Tool")
        
        st.markdown("""
        <div class="mobile-card">
            <h3>District Risk Assessment</h3>
            <p>Enter basic indicators to get a quick risk assessment</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            stunted_pct = st.slider("Stunting %", 0, 50, 15)
            underweight_pct = st.slider("Underweight %", 0, 50, 10)
        
        with col2:
            wasted_pct = st.slider("Wasting %", 0, 50, 5)
            vitamin_a_pct = st.slider("Vitamin A Deficiency %", 0, 50, 8)
        
        # Calculate risk score
        risk_score = (stunted_pct * 0.4 + underweight_pct * 0.3 + wasted_pct * 0.2 + vitamin_a_pct * 0.1)
        
        if risk_score > 20:
            risk_level = "High"
            risk_color = "🔴"
            recommendations = [
                "Immediate intervention required",
                "Vitamin A supplementation program",
                "Nutritional counseling",
                "Mobile health clinics"
            ]
        elif risk_score > 10:
            risk_level = "Medium"
            risk_color = "🟡"
            recommendations = [
                "Preventive measures needed",
                "Community nutrition education",
                "School feeding programs",
                "Agricultural support"
            ]
        else:
            risk_level = "Low"
            risk_color = "🟢"
            recommendations = [
                "Maintain current programs",
                "Monitor trends",
                "Community awareness",
                "Preventive care"
            ]
        
        # Display results
        st.markdown(f"""
        <div class="mobile-card">
            <h3>Assessment Result</h3>
            <p><strong>Risk Level:</strong> {risk_color} {risk_level}</p>
            <p><strong>Risk Score:</strong> {risk_score:.1f}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.subheader("📋 Recommendations")
        for rec in recommendations:
            st.markdown(f"• {rec}")
    
    def render_emergency_alerts(self):
        """Render emergency alerts for high-risk areas"""
        st.subheader("🚨 Emergency Alerts")
        
        # Filter high-risk districts
        if "predicted_risk_level" in self.data.columns:
            high_risk = self.data[self.data["predicted_risk_level"] == "High"]
        else:
            # Fallback: use stunting percentage
            high_risk = self.data[self.data["Stunted_pct"] > self.data["Stunted_pct"].quantile(0.8)]
        
        if len(high_risk) > 0:
            for idx, (_, district) in enumerate(high_risk.head(5).iterrows()):
                st.markdown(f"""
                <div class="mobile-card" style="border-left-color: #e74c3c;">
                    <h3>🚨 {district['District']}</h3>
                    <p><strong>Status:</strong> High Risk Alert</p>
                    <p><strong>Children Affected:</strong> {district['Children_Under5']:,}</p>
                    <p><strong>Action Required:</strong> Immediate intervention</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No high-risk alerts at this time.")
    
    def render_offline_features(self):
        """Render offline-capable features"""
        st.subheader("📱 Offline Features")
        
        # Data export
        st.markdown("""
        <div class="mobile-card">
            <h3>📤 Export Data</h3>
            <p>Download data for offline use</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Download CSV", key="download_csv"):
            csv = self.data.to_csv(index=False)
            st.download_button(
                label="Download Data",
                data=csv,
                file_name=f"malnutrition_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
        # Offline calculator
        st.markdown("""
        <div class="mobile-card">
            <h3>🧮 Offline Calculator</h3>
            <p>Calculate malnutrition indicators offline</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            children = st.number_input("Children Under 5", min_value=0, value=100)
            stunted = st.number_input("Stunted Children", min_value=0, value=15)
        
        with col2:
            underweight = st.number_input("Underweight Children", min_value=0, value=10)
            wasted = st.number_input("Wasted Children", min_value=0, value=5)
        
        if children > 0:
            stunting_rate = (stunted / children) * 100
            underweight_rate = (underweight / children) * 100
            wasting_rate = (wasted / children) * 100
            
            st.metric("Stunting Rate", f"{stunting_rate:.1f}%")
            st.metric("Underweight Rate", f"{underweight_rate:.1f}%")
            st.metric("Wasting Rate", f"{wasting_rate:.1f}%")
    
    def render_mobile_navigation(self):
        """Render mobile navigation"""
        st.markdown("""
        <div class="mobile-nav">
            <a href="#" class="nav-item active">
                <div class="nav-icon">📊</div>
                <div>Dashboard</div>
            </a>
            <a href="#" class="nav-item">
                <div class="nav-icon">🔍</div>
                <div>Search</div>
            </a>
            <a href="#" class="nav-item">
                <div class="nav-icon">⚡</div>
                <div>Assess</div>
            </a>
            <a href="#" class="nav-item">
                <div class="nav-icon">🚨</div>
                <div>Alerts</div>
            </a>
            <a href="#" class="nav-item">
                <div class="nav-icon">📱</div>
                <div>Offline</div>
            </a>
        </div>
        """, unsafe_allow_html=True)
    
    def run(self):
        """Main mobile app runner"""
        self.render_mobile_header()
        self.render_offline_indicator()
        
        # Mobile navigation tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Dashboard", "🔍 Search", "⚡ Assess", "🚨 Alerts", "📱 Offline"])
        
        with tab1:
            self.render_quick_stats()
            
            # Simple chart
            if "Stunted_pct" in self.data.columns:
                fig = px.bar(
                    self.data.head(10),
                    x="District",
                    y="Stunted_pct",
                    title="Top 10 Districts by Stunting Rate",
                    height=300
                )
                fig.update_xaxes(tickangle=45)
                st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            self.render_district_selector()
        
        with tab3:
            self.render_quick_assessment()
        
        with tab4:
            self.render_emergency_alerts()
        
        with tab5:
            self.render_offline_features()
        
        # Mobile navigation (hidden on desktop)
        st.markdown('<div class="mobile-only">', unsafe_allow_html=True)
        self.render_mobile_navigation()
        st.markdown('</div>', unsafe_allow_html=True)

# Run the mobile app
if __name__ == "__main__":
    app = MobileMalnutritionApp()
    app.run()
