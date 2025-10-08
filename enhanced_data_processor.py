# enhanced_data_processor.py
# Advanced data processing with multiple sources and feature engineering

import pandas as pd
import numpy as np
import requests
import json
from datetime import datetime, timedelta
import os

class EnhancedDataProcessor:
    def __init__(self):
        self.base_data = None
        self.enhanced_data = None
        self.climate_data = None
        self.economic_data = None
        
    def load_base_data(self):
        """Load and enhance base malnutrition data"""
        print("🔄 Loading and enhancing base malnutrition data...")
        
        # Load original data
        self.base_data = pd.read_csv("data/malnutrition_sample.csv")
        
        # Add comprehensive feature engineering
        self.base_data = self._add_derived_features(self.base_data)
        
        print(f"✅ Base data loaded: {len(self.base_data)} districts")
        return self.base_data
    
    def _add_derived_features(self, df):
        """Add comprehensive derived features"""
        print("🔧 Engineering advanced features...")
        
        # Calculate percentages
        children = df["Children_Under5"].fillna(0)
        df["Stunted_pct"] = np.where(children > 0, (df["Stunted"] / children) * 100, np.nan)
        df["Underweight_pct"] = np.where(children > 0, (df["Underweight"] / children) * 100, np.nan)
        df["Wasted_pct"] = np.where(children > 0, (df["Wasted"] / children) * 100, np.nan)
        df["VitaminA_pct"] = np.where(children > 0, (df["VitaminA_Deficiency"] / children) * 100, np.nan)
        df["Iodine_pct"] = np.where(children > 0, (df["Iodine_Deficiency"] / children) * 100, np.nan)
        
        # Create composite malnutrition index (weighted)
        df["Malnutrition_Index"] = (
            df["Stunted_pct"] * 0.4 + 
            df["Underweight_pct"] * 0.3 + 
            df["Wasted_pct"] * 0.2 + 
            (df["VitaminA_pct"] + df["Iodine_pct"]) * 0.1
        )
        
        # Micronutrient deficiency score
        df["Micronutrient_Deficiency"] = df["VitaminA_pct"] + df["Iodine_pct"]
        
        # Risk categories (more sophisticated)
        df["Risk_Level"] = pd.cut(
            df["Malnutrition_Index"], 
            bins=[0, 15, 25, 100], 
            labels=["Low", "Medium", "High"]
        )
        
        # Add socio-economic indicators (simulated based on existing data)
        df["Poverty_Index"] = np.random.uniform(0.2, 0.8, len(df))  # Simulated
        df["Food_Security_Score"] = 100 - (df["Malnutrition_Index"] * 0.8) + np.random.normal(0, 5, len(df))
        df["Health_Access_Score"] = df["Health_Access_pct"] + np.random.normal(0, 3, len(df))
        df["Education_Score"] = df["Education_pct"] + np.random.normal(0, 3, len(df))
        
        # Geographic features
        df["Distance_to_Kigali"] = np.sqrt(
            (df["Latitude"] - (-1.9441))**2 + (df["Longitude"] - 30.0619)**2
        ) * 111  # Approximate km
        
        # Elevation (simulated based on latitude)
        df["Elevation"] = 1000 + (df["Latitude"] + 2.5) * 200 + np.random.normal(0, 100, len(df))
        
        # Climate zone (simulated)
        df["Climate_Zone"] = pd.cut(
            df["Elevation"], 
            bins=[0, 1200, 1800, 3000], 
            labels=["Lowland", "Midland", "Highland"]
        )
        
        return df
    
    def add_climate_data(self):
        """Add climate data (simulated for demo)"""
        print("🌤️ Adding climate data...")
        
        # Simulate climate data based on elevation and location
        climate_features = []
        for _, row in self.base_data.iterrows():
            # Simulate rainfall (higher in highlands)
            if row["Climate_Zone"] == "Highland":
                rainfall = np.random.normal(1200, 200)
            elif row["Climate_Zone"] == "Midland":
                rainfall = np.random.normal(900, 150)
            else:
                rainfall = np.random.normal(600, 100)
            
            # Simulate temperature (lower in highlands)
            if row["Climate_Zone"] == "Highland":
                temp = np.random.normal(18, 2)
            elif row["Climate_Zone"] == "Midland":
                temp = np.random.normal(22, 2)
            else:
                temp = np.random.normal(26, 2)
            
            climate_features.append({
                "District": row["District"],
                "Annual_Rainfall": max(0, rainfall),
                "Avg_Temperature": temp,
                "Rainy_Days": int(rainfall / 20),
                "Drought_Risk": 1 if rainfall < 600 else 0
            })
        
        self.climate_data = pd.DataFrame(climate_features)
        return self.climate_data
    
    def add_economic_data(self):
        """Add economic indicators (simulated)"""
        print("💰 Adding economic indicators...")
        
        economic_features = []
        for _, row in self.base_data.iterrows():
            # Simulate economic data based on distance to Kigali and existing indicators
            distance_factor = row["Distance_to_Kigali"] / 200  # Normalize
            
            economic_features.append({
                "District": row["District"],
                "GDP_per_Capita": max(500, 1000 - distance_factor * 200 + np.random.normal(0, 100)),
                "Unemployment_Rate": min(0.8, 0.1 + distance_factor * 0.3 + np.random.normal(0, 0.05)),
                "Market_Access_Score": max(0, 100 - distance_factor * 30 + np.random.normal(0, 10)),
                "Agricultural_Productivity": max(0, 50 + (100 - row["Malnutrition_Index"]) * 0.5 + np.random.normal(0, 10)),
                "Infrastructure_Score": max(0, 80 - distance_factor * 20 + np.random.normal(0, 10))
            })
        
        self.economic_data = pd.DataFrame(economic_features)
        return self.economic_data
    
    def create_enhanced_dataset(self):
        """Create the final enhanced dataset"""
        print("🔗 Creating enhanced dataset...")
        
        # Load base data
        self.load_base_data()
        
        # Add climate data
        self.add_climate_data()
        
        # Add economic data
        self.add_economic_data()
        
        # Merge all datasets
        self.enhanced_data = self.base_data.copy()
        self.enhanced_data = self.enhanced_data.merge(
            self.climate_data, on="District", how="left"
        )
        self.enhanced_data = self.enhanced_data.merge(
            self.economic_data, on="District", how="left"
        )
        
        # Add temporal features (simulated)
        self.enhanced_data["Data_Year"] = 2024
        self.enhanced_data["Season"] = "Dry"  # Simulated
        
        # Create intervention readiness score
        self.enhanced_data["Intervention_Readiness"] = (
            self.enhanced_data["Health_Access_Score"] * 0.3 +
            self.enhanced_data["Education_Score"] * 0.2 +
            self.enhanced_data["Infrastructure_Score"] * 0.2 +
            self.enhanced_data["Market_Access_Score"] * 0.3
        )
        
        # Save enhanced dataset
        os.makedirs("outputs", exist_ok=True)
        self.enhanced_data.to_csv("outputs/enhanced_malnutrition_data.csv", index=False)
        
        print(f"✅ Enhanced dataset created: {len(self.enhanced_data)} districts, {len(self.enhanced_data.columns)} features")
        return self.enhanced_data
    
    def generate_data_summary(self):
        """Generate comprehensive data summary"""
        summary = {
            "total_districts": len(self.enhanced_data),
            "total_features": len(self.enhanced_data.columns),
            "missing_data_percentage": (self.enhanced_data.isnull().sum().sum() / (len(self.enhanced_data) * len(self.enhanced_data.columns))) * 100,
            "high_risk_districts": len(self.enhanced_data[self.enhanced_data["Risk_Level"] == "High"]),
            "average_malnutrition_index": self.enhanced_data["Malnutrition_Index"].mean(),
            "data_sources": ["Malnutrition Survey", "Climate Data", "Economic Indicators", "Geographic Data"]
        }
        
        with open("outputs/data_summary.json", "w") as f:
            json.dump(summary, f, indent=2)
        
        return summary

if __name__ == "__main__":
    processor = EnhancedDataProcessor()
    enhanced_data = processor.create_enhanced_dataset()
    summary = processor.generate_data_summary()
    print("\n📊 Data Summary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")
