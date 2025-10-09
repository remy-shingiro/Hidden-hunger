# enhanced_dashboard.py
# Multi-page, mobile-responsive dashboard with advanced features

import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
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
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .header-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .header-subtitle {
        font-size: 1.2rem;
        opacity: 0.9;
        font-weight: 300;
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
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin-bottom: 2rem;
    }
    
    .nav-button {
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        margin: 0.25rem;
        cursor: pointer;
        transition: all 0.2s ease;
        font-weight: 500;
    }
    
    .nav-button:hover {
        background: #667eea;
        color: white;
        border-color: #667eea;
    }
    
    .nav-button.active {
        background: #667eea;
        color: white;
        border-color: #667eea;
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
        .header-title {
            font-size: 1.8rem;
        }
        .metric-value {
            font-size: 1.5rem;
        }
        .nav-button {
            padding: 0.5rem 1rem;
            font-size: 0.9rem;
        }
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb {
        background: #667eea;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #5a6fd8;
    }
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
        st.markdown("""
        <div class="header-container">
            <div class="header-title">🇷🇼 Rwanda Malnutrition Intelligence Platform</div>
            <div class="header-subtitle">Ending Hidden Hunger Through Data-Driven Solutions</div>
        </div>
        """, unsafe_allow_html=True)
    
    def render_navigation(self):
        """Render navigation menu"""
        st.markdown('<div class="nav-container">', unsafe_allow_html=True)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            if st.button("📊 Dashboard", key="nav_dashboard"):
                st.session_state.current_page = "dashboard"
                st.rerun()
        
        with col2:
            if st.button("🗺️ Interactive Map", key="nav_map"):
                st.session_state.current_page = "map"
                st.rerun()
        
        with col3:
            if st.button("🤖 AI Predictions", key="nav_predictions"):
                st.session_state.current_page = "predictions"
                st.rerun()
        
        with col4:
            if st.button("📋 Policy Briefs", key="nav_policy"):
                st.session_state.current_page = "policy"
                st.rerun()
        
        with col5:
            if st.button("📈 Analytics", key="nav_analytics"):
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
        
        # Top 5 high-risk districts
        st.subheader("🚨 Top 5 High-Risk Districts")
        high_risk_districts = self.data[self.data["predicted_risk_level"] == "High"].nlargest(5, "risk_probability")
        
        for idx, (_, district) in enumerate(high_risk_districts.iterrows(), 1):
            risk_class = "alert-high" if district["risk_probability"] > 0.8 else "alert-medium"
            st.markdown(f"""
            <div class="alert {risk_class}">
                <strong>{idx}. {district['District']}</strong><br>
                Risk Probability: {district['risk_probability']:.1%} | 
                Malnutrition Index: {district['Malnutrition_Index']:.1f} | 
                Children Affected: {district['Children_Under5']:,}
            </div>
            """, unsafe_allow_html=True)
    
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
        
        # Create map
        m = folium.Map(
            location=[-1.95, 30.06], 
            zoom_start=8, 
            tiles=map_style
        )
        
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
        
        # Add GeoJSON (use cached string for speed)
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
        
        # Display map
        st_folium(m, width=1000, height=600)
        
        # Map statistics
        st.subheader("Map Statistics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Districts", len(self.geo_data))
        
        with col2:
            high_risk_count = len(self.geo_data[self.geo_data["predicted_risk_level"] == "High"])
            st.metric("High Risk Districts", high_risk_count)
        
        with col3:
            # Convert risk_probability to numeric for calculation
            risk_probs = pd.to_numeric(self.geo_data['risk_probability'], errors='coerce').fillna(0)
            avg_risk = risk_probs.mean()
            st.metric("Average Risk Probability", f"{avg_risk:.1%}")
    
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
            
            # Cost-benefit analysis
            st.subheader("Cost-Benefit Analysis")
            
            estimated_cost = district_data["Children_Under5"] * 50  # $50 per child
            potential_benefit = district_data["Children_Under5"] * 200  # $200 benefit per child
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Estimated Cost", f"${estimated_cost:,}")
            
            with col2:
                st.metric("Potential Benefit", f"${potential_benefit:,}")
            
            with col3:
                st.metric("ROI", f"{(potential_benefit/estimated_cost-1)*100:.0f}%")
    
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
        self.render_navigation()
        
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
