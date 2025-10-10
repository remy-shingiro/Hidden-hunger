# main.py
# Main entry point for Rwanda Malnutrition Intelligence Platform

import subprocess
import sys
import os

def main():
    """Main entry point - launches the enhanced dashboard"""
    print("🇷🇼 Rwanda Malnutrition Intelligence Platform")
    print("NISR Big Data Hackathon 2025")
    print("=" * 50)
    
    # Check if enhanced data exists
    if not os.path.exists("outputs/enhanced_malnutrition_data.csv"):
        print("Creating enhanced dataset...")
        try:
            subprocess.run([sys.executable, "enhanced_data_processor.py"], check=True)
            print("✅ Enhanced data created successfully")
        except subprocess.CalledProcessError:
            print("⚠️ Warning: Could not create enhanced data, using basic data")
    
    # Check if models exist
    if not os.path.exists("models/ensemble_model.pkl"):
        print("Training ML models...")
        try:
            subprocess.run([sys.executable, "advanced_ml_pipeline.py"], check=True)
            print("✅ ML models trained successfully")
        except subprocess.CalledProcessError:
            print("⚠️ Warning: Could not train models, using basic predictions")
    
    print("\n🚀 Starting Enhanced Dashboard...")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "enhanced_dashboard.py"])

if __name__ == "__main__":
    main()
