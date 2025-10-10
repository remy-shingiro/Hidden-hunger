# realtime_integration.py
# Real-time data integration and API system

import streamlit as st
import pandas as pd
import numpy as np
import requests
import json
from datetime import datetime, timedelta
import time
import threading
import queue
import os
from typing import Dict, List, Optional

class RealTimeDataIntegration:
    def __init__(self):
        self.data_queue = queue.Queue()
        self.update_interval = 300  # 5 minutes
        self.last_update = None
        self.cached_data = None
        self.api_endpoints = {
            "weather": "https://api.openweathermap.org/data/2.5/weather",
            "news": "https://newsapi.org/v2/everything",
            "health_alerts": "https://api.example.com/health-alerts"  # Placeholder
        }
    
    def simulate_real_time_data(self):
        """Simulate real-time data updates"""
        print("🔄 Simulating real-time data updates...")
        
        # Simulate new data points
        new_data = {
            "timestamp": datetime.now(),
            "district": np.random.choice(["Kigali", "Huye", "Musanze", "Rubavu", "Nyagatare"]),
            "malnutrition_index": np.random.normal(20, 5),
            "stunting_rate": np.random.normal(15, 3),
            "underweight_rate": np.random.normal(10, 2),
            "wasting_rate": np.random.normal(5, 1),
            "vitamin_a_deficiency": np.random.normal(8, 2),
            "iodine_deficiency": np.random.normal(7, 2),
            "temperature": np.random.normal(22, 3),
            "rainfall": np.random.exponential(5),
            "drought_risk": np.random.choice([0, 1], p=[0.8, 0.2]),
            "health_facility_access": np.random.normal(80, 10),
            "market_access": np.random.normal(75, 15),
            "education_score": np.random.normal(85, 8)
        }
        
        return new_data
    
    def fetch_weather_data(self, lat: float, lon: float) -> Dict:
        """Fetch real weather data (simulated for demo)"""
        # In a real implementation, you would use actual weather API
        weather_data = {
            "temperature": np.random.normal(22, 3),
            "humidity": np.random.normal(70, 10),
            "rainfall": np.random.exponential(5),
            "wind_speed": np.random.exponential(5),
            "pressure": np.random.normal(1013, 10),
            "description": np.random.choice(["clear", "cloudy", "rainy", "stormy"]),
            "timestamp": datetime.now()
        }
        return weather_data
    
    def fetch_news_data(self, query: str = "malnutrition Rwanda") -> List[Dict]:
        """Fetch relevant news data (simulated for demo)"""
        # In a real implementation, you would use actual news API
        news_items = [
            {
                "title": "Rwanda Launches New Nutrition Program",
                "description": "Government announces new initiative to combat malnutrition in rural areas",
                "source": "Rwanda Today",
                "published_at": datetime.now() - timedelta(hours=2),
                "url": "https://example.com/news1",
                "relevance_score": 0.9
            },
            {
                "title": "Climate Change Affects Food Security",
                "description": "Drought conditions impact agricultural productivity in Eastern Province",
                "source": "East African News",
                "published_at": datetime.now() - timedelta(hours=6),
                "url": "https://example.com/news2",
                "relevance_score": 0.8
            },
            {
                "title": "Mobile Health Clinics Expand Coverage",
                "description": "New mobile health units reach remote communities",
                "source": "Health Rwanda",
                "published_at": datetime.now() - timedelta(hours=12),
                "url": "https://example.com/news3",
                "relevance_score": 0.7
            }
        ]
        return news_items
    
    def fetch_health_alerts(self) -> List[Dict]:
        """Fetch health alerts and notifications (simulated for demo)"""
        alerts = [
            {
                "id": "ALERT_001",
                "type": "high_risk",
                "district": "Rubavu",
                "message": "High malnutrition risk detected in Rubavu District",
                "severity": "high",
                "timestamp": datetime.now() - timedelta(minutes=30),
                "action_required": "Immediate intervention needed",
                "contact": "health@rubavu.gov.rw"
            },
            {
                "id": "ALERT_002",
                "type": "weather_warning",
                "district": "Nyagatare",
                "message": "Drought conditions may affect food security",
                "severity": "medium",
                "timestamp": datetime.now() - timedelta(hours=2),
                "action_required": "Monitor food supplies",
                "contact": "agriculture@nyagatare.gov.rw"
            },
            {
                "id": "ALERT_003",
                "type": "supply_shortage",
                "district": "Huye",
                "message": "Vitamin A supplements running low",
                "severity": "medium",
                "timestamp": datetime.now() - timedelta(hours=4),
                "action_required": "Restock supplies",
                "contact": "supplies@huye.gov.rw"
            }
        ]
        return alerts
    
    def process_real_time_data(self, data: Dict) -> Dict:
        """Process and analyze real-time data"""
        # Calculate risk score
        risk_factors = [
            data.get("malnutrition_index", 0),
            data.get("stunting_rate", 0),
            data.get("underweight_rate", 0),
            data.get("wasting_rate", 0),
            data.get("vitamin_a_deficiency", 0),
            data.get("iodine_deficiency", 0)
        ]
        
        risk_score = np.mean(risk_factors)
        
        # Determine risk level
        if risk_score > 20:
            risk_level = "High"
        elif risk_score > 10:
            risk_level = "Medium"
        else:
            risk_level = "Low"
        
        # Add processed data
        data["risk_score"] = risk_score
        data["risk_level"] = risk_level
        data["processed_at"] = datetime.now()
        
        return data
    
    def update_dashboard_data(self):
        """Update dashboard with real-time data"""
        print("🔄 Updating dashboard data...")
        
        # Get new data
        new_data = self.simulate_real_time_data()
        processed_data = self.process_real_time_data(new_data)
        
        # Update cache
        self.cached_data = processed_data
        self.last_update = datetime.now()
        
        # Store in queue for real-time updates
        self.data_queue.put(processed_data)
        
        return processed_data
    
    def get_live_metrics(self) -> Dict:
        """Get live metrics for dashboard"""
        if self.cached_data is None:
            self.update_dashboard_data()
        
        return {
            "last_update": self.last_update,
            "current_risk_level": self.cached_data.get("risk_level", "Unknown"),
            "risk_score": self.cached_data.get("risk_score", 0),
            "malnutrition_index": self.cached_data.get("malnutrition_index", 0),
            "temperature": self.cached_data.get("temperature", 0),
            "rainfall": self.cached_data.get("rainfall", 0),
            "drought_risk": self.cached_data.get("drought_risk", 0)
        }
    
    def render_real_time_dashboard(self):
        """Render real-time dashboard components"""
        st.header("🔄 Real-Time Monitoring")
        
        # Auto-refresh toggle
        auto_refresh = st.checkbox("Enable Auto-Refresh", value=True)
        
        if auto_refresh:
            # Auto-refresh every 30 seconds
            time.sleep(30)
            st.rerun()
        
        # Manual refresh button
        if st.button("🔄 Refresh Data", key="refresh_data"):
            self.update_dashboard_data()
            st.rerun()
        
        # Live metrics
        metrics = self.get_live_metrics()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Current Risk Level",
                metrics["current_risk_level"],
                delta=f"Score: {metrics['risk_score']:.1f}"
            )
        
        with col2:
            st.metric(
                "Malnutrition Index",
                f"{metrics['malnutrition_index']:.1f}",
                delta="Live"
            )
        
        with col3:
            st.metric(
                "Temperature",
                f"{metrics['temperature']:.1f}°C",
                delta="Current"
            )
        
        with col4:
            st.metric(
                "Rainfall",
                f"{metrics['rainfall']:.1f}mm",
                delta="Today"
            )
        
        # Last update time
        if metrics["last_update"]:
            st.info(f"Last updated: {metrics['last_update'].strftime('%Y-%m-%d %H:%M:%S')}")
    
    def render_health_alerts(self):
        """Render health alerts dashboard"""
        st.header("🚨 Health Alerts & Notifications")
        
        alerts = self.fetch_health_alerts()
        
        for alert in alerts:
            severity_color = {
                "high": "🔴",
                "medium": "🟡",
                "low": "🟢"
            }.get(alert["severity"], "⚪")
            
            with st.expander(f"{severity_color} {alert['type'].replace('_', ' ').title()} - {alert['district']}"):
                st.write(f"**Message:** {alert['message']}")
                st.write(f"**Severity:** {alert['severity'].title()}")
                st.write(f"**Time:** {alert['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
                st.write(f"**Action Required:** {alert['action_required']}")
                st.write(f"**Contact:** {alert['contact']}")
                
                if st.button(f"Mark as Read", key=f"alert_{alert['id']}"):
                    st.success("Alert marked as read")
    
    def render_news_feed(self):
        """Render news feed"""
        st.header("📰 News & Updates")
        
        news_items = self.fetch_news_data()
        
        for item in news_items:
            with st.expander(f"📰 {item['title']}"):
                st.write(f"**Source:** {item['source']}")
                st.write(f"**Published:** {item['published_at'].strftime('%Y-%m-%d %H:%M:%S')}")
                st.write(f"**Description:** {item['description']}")
                st.write(f"**Relevance Score:** {item['relevance_score']:.1f}")
                
                if st.button(f"Read More", key=f"news_{item['title'][:20]}"):
                    st.info(f"Opening: {item['url']}")
    
    def render_weather_monitoring(self):
        """Render weather monitoring"""
        st.header("🌤️ Weather Monitoring")
        
        # Get weather data for different districts
        districts = [
            {"name": "Kigali", "lat": -1.9441, "lon": 30.0619},
            {"name": "Huye", "lat": -2.586, "lon": 29.739},
            {"name": "Musanze", "lat": -1.501, "lon": 29.632},
            {"name": "Rubavu", "lat": -1.748, "lon": 29.259},
            {"name": "Nyagatare", "lat": -1.285, "lon": 30.326}
        ]
        
        for district in districts:
            weather = self.fetch_weather_data(district["lat"], district["lon"])
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(f"{district['name']} Temperature", f"{weather['temperature']:.1f}°C")
            
            with col2:
                st.metric("Humidity", f"{weather['humidity']:.1f}%")
            
            with col3:
                st.metric("Rainfall", f"{weather['rainfall']:.1f}mm")
        
        # Weather impact analysis
        st.subheader("Weather Impact Analysis")
        
        # Simulate weather impact on malnutrition
        weather_impact_data = pd.DataFrame({
            "District": [d["name"] for d in districts],
            "Temperature": [self.fetch_weather_data(d["lat"], d["lon"])["temperature"] for d in districts],
            "Rainfall": [self.fetch_weather_data(d["lat"], d["lon"])["rainfall"] for d in districts],
            "Malnutrition_Risk": np.random.normal(20, 5, len(districts))
        })
        
        fig = px.scatter(
            weather_impact_data,
            x="Temperature",
            y="Malnutrition_Risk",
            size="Rainfall",
            color="District",
            title="Temperature vs Malnutrition Risk",
            hover_data=["Rainfall"]
        )
        st.plotly_chart(fig, use_container_width=True)
    
    def render_api_status(self):
        """Render API status and connectivity"""
        st.header("🔌 API Status & Connectivity")
        
        # Check API endpoints
        api_status = {}
        
        for name, endpoint in self.api_endpoints.items():
            try:
                # Simulate API check
                response_time = np.random.uniform(0.1, 2.0)
                status = "🟢 Online" if response_time < 1.0 else "🟡 Slow" if response_time < 2.0 else "🔴 Offline"
                
                api_status[name] = {
                    "status": status,
                    "response_time": f"{response_time:.2f}s",
                    "endpoint": endpoint
                }
            except Exception as e:
                api_status[name] = {
                    "status": "🔴 Offline",
                    "response_time": "N/A",
                    "endpoint": endpoint,
                    "error": str(e)
                }
        
        # Display API status
        for name, status in api_status.items():
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"**{name.title()} API**")
            
            with col2:
                st.write(status["status"])
            
            with col3:
                st.write(status["response_time"])
        
        # Data freshness indicator
        st.subheader("Data Freshness")
        
        if self.last_update:
            time_since_update = datetime.now() - self.last_update
            freshness = "🟢 Fresh" if time_since_update.total_seconds() < 300 else "🟡 Stale" if time_since_update.total_seconds() < 1800 else "🔴 Outdated"
            
            st.write(f"**Status:** {freshness}")
            st.write(f"**Last Update:** {self.last_update.strftime('%Y-%m-%d %H:%M:%S')}")
            st.write(f"**Time Since Update:** {time_since_update}")
        else:
            st.write("**Status:** 🔴 No Data")
    
    def run_real_time_dashboard(self):
        """Run the complete real-time dashboard"""
        st.title("🔄 Real-Time Malnutrition Monitoring")
        
        # Navigation
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Live Metrics", "🚨 Alerts", "📰 News", "🌤️ Weather", "🔌 API Status"
        ])
        
        with tab1:
            self.render_real_time_dashboard()
        
        with tab2:
            self.render_health_alerts()
        
        with tab3:
            self.render_news_feed()
        
        with tab4:
            self.render_weather_monitoring()
        
        with tab5:
            self.render_api_status()

# Run the real-time dashboard
if __name__ == "__main__":
    rt_integration = RealTimeDataIntegration()
    rt_integration.run_real_time_dashboard()
