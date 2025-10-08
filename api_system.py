# api_system.py
# RESTful API system for external integrations

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import joblib
import json
from datetime import datetime, timedelta
import os
from typing import Dict, List, Optional

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

class MalnutritionAPI:
    def __init__(self):
        self.data = None
        self.models = {}
        self.load_data()
        self.load_models()
    
    def load_data(self):
        """Load enhanced data"""
        try:
            self.data = pd.read_csv("outputs/enhanced_malnutrition_data.csv")
            print("✅ Data loaded successfully")
        except FileNotFoundError:
            print("❌ Enhanced data not found")
            self.data = None
    
    def load_models(self):
        """Load trained models"""
        try:
            self.models['ensemble'] = joblib.load("models/ensemble_model.pkl")
            self.models['scaler'] = joblib.load("models/scaler.pkl")
            print("✅ Models loaded successfully")
        except FileNotFoundError:
            print("❌ Models not found")
            self.models = {}
    
    def predict_risk(self, district_data: Dict) -> Dict:
        """Predict malnutrition risk for a district"""
        if not self.models or self.data is None:
            return {"error": "Models not available"}
        
        try:
            # Prepare features
            features = [
                district_data.get("Underweight_pct", 0),
                district_data.get("Wasted_pct", 0),
                district_data.get("VitaminA_pct", 0),
                district_data.get("Iodine_pct", 0),
                district_data.get("Malnutrition_Index", 0),
                district_data.get("Micronutrient_Deficiency", 0),
                district_data.get("Poverty_Index", 0),
                district_data.get("Food_Security_Score", 0),
                district_data.get("Health_Access_Score", 0),
                district_data.get("Education_Score", 0),
                district_data.get("Distance_to_Kigali", 0),
                district_data.get("Elevation", 0),
                district_data.get("Annual_Rainfall", 0),
                district_data.get("Avg_Temperature", 0),
                district_data.get("Drought_Risk", 0),
                district_data.get("GDP_per_Capita", 0),
                district_data.get("Unemployment_Rate", 0),
                district_data.get("Market_Access_Score", 0),
                district_data.get("Agricultural_Productivity", 0),
                district_data.get("Infrastructure_Score", 0),
                district_data.get("Intervention_Readiness", 0)
            ]
            
            # Scale features
            X = np.array(features).reshape(1, -1)
            X_scaled = self.models['scaler'].transform(X)
            
            # Make prediction
            prediction = self.models['ensemble'].predict(X_scaled)[0]
            probability = self.models['ensemble'].predict_proba(X_scaled)[0][1]
            
            # Determine risk level
            if probability > 0.7:
                risk_level = "High"
            elif probability > 0.3:
                risk_level = "Medium"
            else:
                risk_level = "Low"
            
            return {
                "prediction": int(prediction),
                "probability": float(probability),
                "risk_level": risk_level,
                "confidence": "High" if abs(probability - 0.5) > 0.3 else "Medium",
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            return {"error": str(e)}

# Initialize API
api = MalnutritionAPI()

@app.route('/')
def home():
    """API home endpoint"""
    return jsonify({
        "message": "Rwanda Malnutrition Intelligence Platform API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "districts": "/districts",
            "predict": "/predict",
            "risk_levels": "/risk-levels",
            "statistics": "/statistics",
            "export": "/export"
        }
    })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "data_loaded": api.data is not None,
        "models_loaded": len(api.models) > 0
    })

@app.route('/districts')
def get_districts():
    """Get all districts with basic information"""
    if api.data is None:
        return jsonify({"error": "Data not available"}), 500
    
    districts = []
    for _, row in api.data.iterrows():
        districts.append({
            "district": row["District"],
            "malnutrition_index": float(row.get("Malnutrition_Index", 0)),
            "risk_level": row.get("predicted_risk_level", "Unknown"),
            "children_under5": int(row.get("Children_Under5", 0)),
            "latitude": float(row.get("Latitude", 0)),
            "longitude": float(row.get("Longitude", 0))
        })
    
    return jsonify({
        "districts": districts,
        "total": len(districts),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/districts/<district_name>')
def get_district_details(district_name):
    """Get detailed information for a specific district"""
    if api.data is None:
        return jsonify({"error": "Data not available"}), 500
    
    district_data = api.data[api.data["District"].str.lower() == district_name.lower()]
    
    if district_data.empty:
        return jsonify({"error": "District not found"}), 404
    
    district = district_data.iloc[0]
    
    return jsonify({
        "district": district["District"],
        "malnutrition_index": float(district.get("Malnutrition_Index", 0)),
        "risk_level": district.get("predicted_risk_level", "Unknown"),
        "risk_probability": float(district.get("risk_probability", 0)),
        "children_under5": int(district.get("Children_Under5", 0)),
        "stunted_pct": float(district.get("Stunted_pct", 0)),
        "underweight_pct": float(district.get("Underweight_pct", 0)),
        "wasted_pct": float(district.get("Wasted_pct", 0)),
        "vitamin_a_pct": float(district.get("VitaminA_pct", 0)),
        "iodine_pct": float(district.get("Iodine_pct", 0)),
        "poverty_index": float(district.get("Poverty_Index", 0)),
        "food_security_score": float(district.get("Food_Security_Score", 0)),
        "health_access_score": float(district.get("Health_Access_Score", 0)),
        "education_score": float(district.get("Education_Score", 0)),
        "latitude": float(district.get("Latitude", 0)),
        "longitude": float(district.get("Longitude", 0)),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/predict', methods=['POST'])
def predict_risk():
    """Predict malnutrition risk for given data"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Validate required fields
        required_fields = ["Underweight_pct", "Wasted_pct", "VitaminA_pct", "Iodine_pct"]
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400
        
        # Make prediction
        result = api.predict_risk(data)
        
        if "error" in result:
            return jsonify(result), 500
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/risk-levels')
def get_risk_levels():
    """Get districts grouped by risk level"""
    if api.data is None:
        return jsonify({"error": "Data not available"}), 500
    
    risk_levels = {}
    
    for level in ["High", "Medium", "Low"]:
        districts = api.data[api.data.get("predicted_risk_level", "Unknown") == level]
        risk_levels[level] = {
            "count": len(districts),
            "districts": districts["District"].tolist(),
            "average_malnutrition_index": float(districts["Malnutrition_Index"].mean()) if len(districts) > 0 else 0
        }
    
    return jsonify({
        "risk_levels": risk_levels,
        "total_districts": len(api.data),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/statistics')
def get_statistics():
    """Get overall statistics"""
    if api.data is None:
        return jsonify({"error": "Data not available"}), 500
    
    stats = {
        "total_districts": len(api.data),
        "total_children_under5": int(api.data["Children_Under5"].sum()),
        "average_malnutrition_index": float(api.data["Malnutrition_Index"].mean()),
        "high_risk_districts": len(api.data[api.data.get("predicted_risk_level", "Unknown") == "High"]),
        "medium_risk_districts": len(api.data[api.data.get("predicted_risk_level", "Unknown") == "Medium"]),
        "low_risk_districts": len(api.data[api.data.get("predicted_risk_level", "Unknown") == "Low"]),
        "average_stunting_rate": float(api.data["Stunted_pct"].mean()),
        "average_underweight_rate": float(api.data["Underweight_pct"].mean()),
        "average_wasting_rate": float(api.data["Wasted_pct"].mean()),
        "average_vitamin_a_deficiency": float(api.data["VitaminA_pct"].mean()),
        "average_iodine_deficiency": float(api.data["Iodine_pct"].mean())
    }
    
    return jsonify({
        "statistics": stats,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/export')
def export_data():
    """Export data in various formats"""
    if api.data is None:
        return jsonify({"error": "Data not available"}), 500
    
    format_type = request.args.get('format', 'json')
    
    if format_type == 'json':
        return jsonify({
            "data": api.data.to_dict('records'),
            "timestamp": datetime.now().isoformat()
        })
    
    elif format_type == 'csv':
        csv_data = api.data.to_csv(index=False)
        return csv_data, 200, {
            'Content-Type': 'text/csv',
            'Content-Disposition': f'attachment; filename=malnutrition_data_{datetime.now().strftime("%Y%m%d")}.csv'
        }
    
    else:
        return jsonify({"error": "Unsupported format. Use 'json' or 'csv'"}), 400

@app.route('/recommendations/<district_name>')
def get_recommendations(district_name):
    """Get policy recommendations for a district"""
    if api.data is None:
        return jsonify({"error": "Data not available"}), 500
    
    district_data = api.data[api.data["District"].str.lower() == district_name.lower()]
    
    if district_data.empty:
        return jsonify({"error": "District not found"}), 404
    
    district = district_data.iloc[0]
    
    # Generate recommendations based on district characteristics
    recommendations = {
        "health": [],
        "agriculture": [],
        "education": []
    }
    
    # Health recommendations
    if district.get("Stunted_pct", 0) > 20:
        recommendations["health"].append("Vitamin A supplementation program")
    if district.get("Underweight_pct", 0) > 15:
        recommendations["health"].append("Nutritional counseling and monitoring")
    if district.get("VitaminA_pct", 0) > 10:
        recommendations["health"].append("Vitamin A supplementation program")
    if district.get("Iodine_pct", 0) > 10:
        recommendations["health"].append("Iodine supplementation program")
    if district.get("Health_Access_Score", 0) < 80:
        recommendations["health"].append("Mobile health clinics")
    
    # Agriculture recommendations
    if district.get("Poverty_Index", 0) > 0.6:
        recommendations["agriculture"].append("Agricultural extension services")
    if district.get("Drought_Risk", 0) == 1:
        recommendations["agriculture"].append("Drought-resistant crop varieties")
    if district.get("Agricultural_Productivity", 0) < 60:
        recommendations["agriculture"].append("Fertilizer and seed programs")
    recommendations["agriculture"].append("Promote biofortified crops")
    recommendations["agriculture"].append("Kitchen garden programs")
    
    # Education recommendations
    if district.get("Education_Score", 0) < 80:
        recommendations["education"].append("Teacher training on nutrition")
    recommendations["education"].append("School feeding programs")
    recommendations["education"].append("Nutrition awareness campaigns")
    recommendations["education"].append("Community nutrition education")
    
    return jsonify({
        "district": district["District"],
        "risk_level": district.get("predicted_risk_level", "Unknown"),
        "recommendations": recommendations,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/alerts')
def get_alerts():
    """Get high-priority alerts"""
    if api.data is None:
        return jsonify({"error": "Data not available"}), 500
    
    alerts = []
    
    # High-risk districts
    high_risk = api.data[api.data.get("predicted_risk_level", "Unknown") == "High"]
    for _, district in high_risk.iterrows():
        alerts.append({
            "type": "high_risk",
            "district": district["District"],
            "message": f"High malnutrition risk detected in {district['District']}",
            "severity": "high",
            "malnutrition_index": float(district.get("Malnutrition_Index", 0)),
            "children_affected": int(district.get("Children_Under5", 0))
        })
    
    # Drought risk
    drought_risk = api.data[api.data.get("Drought_Risk", 0) == 1]
    for _, district in drought_risk.iterrows():
        alerts.append({
            "type": "drought_risk",
            "district": district["District"],
            "message": f"Drought conditions may affect food security in {district['District']}",
            "severity": "medium",
            "rainfall": float(district.get("Annual_Rainfall", 0))
        })
    
    return jsonify({
        "alerts": alerts,
        "total_alerts": len(alerts),
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚀 Starting Rwanda Malnutrition API Server...")
    print("📊 API Documentation available at: http://localhost:5000/")
    print("🔗 Health check: http://localhost:5000/health")
    print("📱 Mobile app integration ready")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
