# run_dashboard.py
# Windows-compatible dashboard launcher

import subprocess
import sys
import os
import time
from datetime import datetime

def main():
    """Main dashboard launcher"""
    print("Rwanda Malnutrition Intelligence Platform")
    print("NISR Big Data Hackathon 2025")
    print("=" * 50)
    
    # Check if enhanced data exists
    if not os.path.exists("outputs/enhanced_malnutrition_data.csv"):
        print("Creating enhanced dataset...")
        try:
            subprocess.run([sys.executable, "enhanced_data_processor.py"], check=True)
            print("Enhanced data created successfully")
        except subprocess.CalledProcessError:
            print("Warning: Could not create enhanced data, using basic data")
    
    # Check if models exist
    if not os.path.exists("models/ensemble_model.pkl"):
        print("Training ML models...")
        try:
            subprocess.run([sys.executable, "advanced_ml_pipeline.py"], check=True)
            print("ML models trained successfully")
        except subprocess.CalledProcessError:
            print("Warning: Could not train models, using basic predictions")
    
    print("\nAvailable Applications:")
    print("1. Main Dashboard (enhanced_dashboard.py)")
    print("2. Mobile App (mobile_app.py)")
    print("3. Real-time Monitor (realtime_integration.py)")
    print("4. API Server (api_system.py)")
    
    choice = input("\nSelect application (1-4) or press Enter for main dashboard: ").strip()
    
    if choice == "2":
        print("Starting Mobile App...")
        subprocess.run([sys.executable, "-m", "streamlit", "run", "mobile_app.py"])
    elif choice == "3":
        print("Starting Real-time Monitor...")
        subprocess.run([sys.executable, "-m", "streamlit", "run", "realtime_integration.py"])
    elif choice == "4":
        print("Starting API Server...")
        subprocess.run([sys.executable, "api_system.py"])
    else:
        print("Starting Main Dashboard...")
        subprocess.run([sys.executable, "-m", "streamlit", "run", "enhanced_dashboard.py"])

if __name__ == "__main__":
    main()
