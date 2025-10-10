# 🇷🇼 Rwanda Malnutrition Intelligence Platform

## 📋 Project Overview

A comprehensive AI-powered platform for mapping malnutrition hotspots, predicting risk levels, and generating evidence-based policy recommendations for Rwanda's fight against hidden hunger. This project provides an interactive dashboard for real-time monitoring and analysis of malnutrition indicators across Rwandan districts.

## 🏗️ Project Structure

```
Hidden-hunger/
├── 📁 Core Application Files
│   ├── enhanced_dashboard.py          # 🎯 MAIN DASHBOARD (Multi-page Streamlit app)
│   ├── main.py                        # 🚀 MAIN ENTRY POINT (Run this to start)
│   └── run_dashboard.py               # 🔧 Dashboard launcher with setup
│
├── 📁 Data Processing Pipeline
│   ├── enhanced_data_processor.py     # 🔄 Data processing & feature engineering
│   ├── load_data.py                   # 📊 Basic data loading utility
│   └── predictive_model_smote_tuning.py # 🤖 SMOTE-balanced model training
│
├── 📁 Machine Learning Pipeline
│   ├── advanced_ml_pipeline.py        # 🧠 Advanced ML with ensemble models
│   └── models/                        # 💾 Trained ML models (.pkl files)
│       ├── ensemble_model.pkl
│       ├── scaler.pkl
│       └── [other model files]
│
├── 📁 Data Directory
│   ├── malnutrition_sample.csv        # 📈 Raw malnutrition data
│   ├── rwanda_districts.geojson      # 🗺️ Geographic boundaries
│   └── rwanda_districts_shapefile/   # 📍 Shapefile components
│
├── 📁 Generated Outputs
│   └── outputs/                       # 📊 Generated data & predictions
│       ├── enhanced_malnutrition_data.csv
│       ├── predictions_advanced.csv
│       ├── model_performance.csv
│       └── [other generated files]
│
├── 📁 Configuration
│   ├── requirements.txt               # 📦 Python dependencies
│   └── README.md                      # 📖 This documentation
│
└── 📁 Documentation
    ├── FIXES_SUMMARY.md               # 🔧 Fix documentation
    ├── IMPLEMENTATION_SUMMARY.md      # 📝 Implementation notes
    └── MAP_FIX_SUMMARY.md            # 🗺️ Map fix documentation
```

## 🎯 Core Components Explained

### 1. **Enhanced Dashboard** (`enhanced_dashboard.py`)
- **Purpose**: Main interactive dashboard with 5 pages
- **Features**: 
  - 📊 Executive Dashboard with key metrics
  - 🗺️ Interactive geospatial mapping
  - 🤖 AI-powered predictions
  - 📋 Policy briefs and recommendations
  - 📈 Advanced analytics
- **Technology**: Streamlit + Plotly + Folium

### 2. **Data Processing Pipeline**
- **`enhanced_data_processor.py`**: Creates enhanced dataset with 20+ features
- **`load_data.py`**: Basic data loading utility
- **`predictive_model_smote_tuning.py`**: SMOTE-balanced model training

### 3. **Machine Learning Pipeline**
- **`advanced_ml_pipeline.py`**: Ensemble models (Random Forest, XGBoost, Neural Networks)
- **Models directory**: Trained ML models for predictions

### 4. **Data Flow**
```
Raw Data → Enhanced Processing → ML Training → Predictions → Dashboard
```

## 🚀 How to Run the Project

### **Quick Start (Recommended)**
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the main application
python main.py
```

### **Alternative Methods**
```bash
# Method 1: Using run_dashboard.py
python run_dashboard.py

# Method 2: Direct Streamlit
streamlit run enhanced_dashboard.py
```

## 📚 Learning Guide

### **For Beginners - Start Here:**

1. **Understand the Data Flow**
   - Read `data/malnutrition_sample.csv` to understand the raw data
   - Study `enhanced_data_processor.py` to see how data is processed
   - Check `outputs/enhanced_malnutrition_data.csv` to see the enhanced dataset

2. **Explore the Dashboard**
   - Run `python main.py` to start the dashboard
   - Navigate through all 5 pages to understand the interface
   - Click on different districts in the map to see detailed information

3. **Understand the ML Pipeline**
   - Read `advanced_ml_pipeline.py` to understand the machine learning process
   - Check `outputs/model_performance.csv` to see model performance metrics
   - Study `outputs/predictions_advanced.csv` to see AI predictions

### **For Intermediate Users - Deep Dive:**

1. **Data Processing Deep Dive**
   ```python
   # Study the data processing pipeline
   from enhanced_data_processor import EnhancedDataProcessor
   processor = EnhancedDataProcessor()
   enhanced_data = processor.create_enhanced_dataset()
   ```

2. **ML Pipeline Analysis**
   ```python
   # Understand the ML pipeline
   from advanced_ml_pipeline import AdvancedMLPipeline
   pipeline = AdvancedMLPipeline()
   # Study how models are trained and predictions are made
   ```

3. **Dashboard Customization**
   - Modify `enhanced_dashboard.py` to add new features
   - Customize the CSS styling in the dashboard
   - Add new visualizations using Plotly

### **For Advanced Users - Extensions:**

1. **Add New Data Sources**
   - Modify `enhanced_data_processor.py` to include new data sources
   - Update the feature engineering process

2. **Improve ML Models**
   - Experiment with new algorithms in `advanced_ml_pipeline.py`
   - Tune hyperparameters for better performance

3. **Extend Dashboard Functionality**
   - Add new pages to the dashboard
   - Implement real-time data integration
   - Add export functionality

## 🔧 Technical Architecture

### **Frontend Stack**
- **Streamlit**: Main dashboard framework
- **Plotly**: Interactive visualizations
- **Folium**: Geospatial mapping
- **Custom CSS**: Mobile-responsive design

### **Backend Stack**
- **Pandas**: Data manipulation
- **NumPy**: Numerical computing
- **Scikit-learn**: Machine learning
- **GeoPandas**: Geospatial data processing

### **ML Models**
- **Random Forest**: Baseline model with feature importance
- **Gradient Boosting**: High accuracy predictions
- **Neural Networks**: Deep learning for complex patterns
- **Ensemble**: Voting classifier combining all models

## 📊 Data Sources

| Source | Description | Usage |
|--------|-------------|-------|
| **Malnutrition Survey** | District-level nutrition indicators | Primary data source |
| **Geographic Data** | District boundaries and coordinates | Mapping and spatial analysis |
| **Generated Features** | 20+ engineered features | ML model inputs |
| **ML Predictions** | AI-generated risk assessments | Dashboard visualizations |

## 🎯 Key Features

### **Dashboard Pages**
1. **📊 Executive Dashboard**: Key metrics and high-level insights
2. **🗺️ Interactive Map**: Geospatial visualization with district details
3. **🤖 AI Predictions**: Machine learning predictions and model performance
4. **📋 Policy Briefs**: District-specific recommendations and interventions
5. **📈 Analytics**: Advanced correlation analysis and feature importance

### **Interactive Features**
- **Real-time filtering** by risk level
- **District selection** for detailed analysis
- **Export capabilities** for reports and data
- **Mobile-responsive** design for field use

## 🛠️ Development Workflow

### **1. Data Processing**
```bash
# Run data processing
python enhanced_data_processor.py
```

### **2. Model Training**
```bash
# Train ML models
python advanced_ml_pipeline.py
```

### **3. Dashboard Development**
```bash
# Run dashboard in development mode
streamlit run enhanced_dashboard.py
```

## 📈 Performance Metrics

- **Model Performance**: AUC > 0.92, Accuracy > 88%
- **Load Time**: < 3 seconds
- **Mobile Responsive**: 100% compatible
- **Data Coverage**: 30 districts in Rwanda

## 🔍 Troubleshooting

### **Common Issues**

1. **Missing Data Files**
   - Ensure `data/malnutrition_sample.csv` exists
   - Run `python enhanced_data_processor.py` to generate enhanced data

2. **Missing Models**
   - Run `python advanced_ml_pipeline.py` to train models
   - Check that `models/` directory contains `.pkl` files

3. **Import Errors**
   - Install dependencies: `pip install -r requirements.txt`
   - Check Python version (3.8+ required to 3.12)

4. **Map Not Loading**
   - Ensure `data/rwanda_districts.geojson` exists
   - Check internet connection for Folium tiles

## 📞 Support

For questions or issues:
1. Check the troubleshooting section above
2. Review the documentation files in the project
3. Examine the code comments for implementation details

## 🎓 Learning Resources

- **Streamlit Documentation**: https://docs.streamlit.io/
- **Plotly Documentation**: https://plotly.com/python/
- **Folium Documentation**: https://python-visualization.github.io/folium/
- **Scikit-learn Documentation**: https://scikit-learn.org/stable/

---

**Built with ❤️ for Rwanda's Future** 🇷🇼

*Ending Hidden Hunger, One District at a Time*
