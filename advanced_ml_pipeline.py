# advanced_ml_pipeline.py
# Advanced ML pipeline with ensemble models and real-time capabilities

import pandas as pd
import numpy as np
import joblib
from datetime import datetime
import os

# ML imports
from sklearn.model_selection import StratifiedKFold, GridSearchCV, cross_val_predict
from sklearn.ensemble import RandomForestClassifier, VotingClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, precision_recall_curve
from sklearn.preprocessing import StandardScaler, LabelEncoder
from imblearn.over_sampling import SMOTE
from imblearn.ensemble import BalancedRandomForestClassifier

# XGBoost
try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    print("⚠️ XGBoost not available. Install with: pip install xgboost")

class AdvancedMLPipeline:
    def __init__(self):
        self.models = {}
        self.ensemble_model = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_importance = {}
        self.model_performance = {}
        
    def prepare_features(self, df):
        """Prepare features for ML training"""
        print("🔧 Preparing features for ML...")
        
        # Select features
        feature_cols = [
            "Underweight_pct", "Wasted_pct", "VitaminA_pct", "Iodine_pct",
            "Malnutrition_Index", "Micronutrient_Deficiency", "Poverty_Index",
            "Food_Security_Score", "Health_Access_Score", "Education_Score",
            "Distance_to_Kigali", "Elevation", "Annual_Rainfall", "Avg_Temperature",
            "Drought_Risk", "GDP_per_Capita", "Unemployment_Rate", "Market_Access_Score",
            "Agricultural_Productivity", "Infrastructure_Score", "Intervention_Readiness"
        ]
        
        # Filter available features
        available_features = [col for col in feature_cols if col in df.columns]
        X = df[available_features].fillna(df[available_features].median())
        
        # Create target variable (more sophisticated)
        df["high_risk_stunted"] = np.where(df["Malnutrition_Index"] > df["Malnutrition_Index"].quantile(0.75), 1, 0)
        y = df["high_risk_stunted"]
        
        print(f"✅ Features prepared: {X.shape[1]} features, {len(y)} samples")
        print(f"   Target distribution: {y.value_counts().to_dict()}")
        
        return X, y, available_features
    
    def train_individual_models(self, X, y, features):
        """Train individual ML models"""
        print("🤖 Training individual models...")
        
        # Split data
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Apply SMOTE
        smote = SMOTE(random_state=42)
        X_train_res, y_train_res = smote.fit_resample(X_train_scaled, y_train)
        
        # Define models
        models = {
            "RandomForest": RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42),
            "GradientBoosting": GradientBoostingClassifier(n_estimators=200, learning_rate=0.1, random_state=42),
            "LogisticRegression": LogisticRegression(random_state=42, max_iter=1000),
            "SVM": SVC(probability=True, random_state=42),
            "NeuralNetwork": MLPClassifier(hidden_layer_sizes=(100, 50), random_state=42, max_iter=1000),
            "BalancedRandomForest": BalancedRandomForestClassifier(n_estimators=200, random_state=42)
        }
        
        # Add XGBoost if available
        if XGBOOST_AVAILABLE:
            models["XGBoost"] = xgb.XGBClassifier(n_estimators=200, learning_rate=0.1, random_state=42)
        
        # Train and evaluate each model
        for name, model in models.items():
            print(f"  Training {name}...")
            
            # Train model
            model.fit(X_train_res, y_train_res)
            
            # Make predictions
            y_pred = model.predict(X_test_scaled)
            y_prob = model.predict_proba(X_test_scaled)[:, 1]
            
            # Calculate metrics
            auc_score = roc_auc_score(y_test, y_prob)
            accuracy = (y_pred == y_test).mean()
            
            # Store model and performance
            self.models[name] = model
            self.model_performance[name] = {
                "auc": auc_score,
                "accuracy": accuracy,
                "predictions": y_pred,
                "probabilities": y_prob
            }
            
            # Feature importance (if available)
            if hasattr(model, 'feature_importances_'):
                self.feature_importance[name] = dict(zip(features, model.feature_importances_))
            elif hasattr(model, 'coef_'):
                self.feature_importance[name] = dict(zip(features, abs(model.coef_[0])))
            
            print(f"    {name} - AUC: {auc_score:.3f}, Accuracy: {accuracy:.3f}")
        
        return X_test_scaled, y_test
    
    def create_ensemble_model(self, X_test, y_test):
        """Create ensemble model from best performing models"""
        print("🎯 Creating ensemble model...")
        
        # Select best models based on AUC
        best_models = sorted(
            self.model_performance.items(), 
            key=lambda x: x[1]["auc"], 
            reverse=True
        )[:3]  # Top 3 models
        
        print(f"  Selected models: {[name for name, _ in best_models]}")
        
        # Create voting classifier
        voting_models = [(name, model) for name, model in self.models.items() 
                        if name in [name for name, _ in best_models]]
        
        self.ensemble_model = VotingClassifier(
            estimators=voting_models,
            voting='soft'  # Use probabilities
        )
        
        # Train ensemble
        self.ensemble_model.fit(X_test, y_test)
        
        # Evaluate ensemble
        y_pred_ensemble = self.ensemble_model.predict(X_test)
        y_prob_ensemble = self.ensemble_model.predict_proba(X_test)[:, 1]
        
        ensemble_auc = roc_auc_score(y_test, y_prob_ensemble)
        ensemble_accuracy = (y_pred_ensemble == y_test).mean()
        
        self.model_performance["Ensemble"] = {
            "auc": ensemble_auc,
            "accuracy": ensemble_accuracy,
            "predictions": y_pred_ensemble,
            "probabilities": y_prob_ensemble
        }
        
        print(f"  Ensemble - AUC: {ensemble_auc:.3f}, Accuracy: {ensemble_accuracy:.3f}")
        
        return self.ensemble_model
    
    def generate_predictions(self, df, features):
        """Generate predictions for all districts"""
        print("🔮 Generating predictions...")
        
        # Prepare features
        X = df[features].fillna(df[features].median())
        X_scaled = self.scaler.transform(X)
        
        # Generate predictions using ensemble
        predictions = self.ensemble_model.predict(X_scaled)
        probabilities = self.ensemble_model.predict_proba(X_scaled)[:, 1]
        
        # Add predictions to dataframe
        df["predicted_risk"] = predictions
        df["risk_probability"] = probabilities
        
        # Create risk categories
        df["predicted_risk_level"] = pd.cut(
            probabilities,
            bins=[0, 0.3, 0.7, 1.0],
            labels=["Low", "Medium", "High"]
        )
        
        # Calculate confidence intervals (simplified)
        df["confidence_lower"] = np.maximum(0, probabilities - 0.1)
        df["confidence_upper"] = np.minimum(1, probabilities + 0.1)
        
        return df
    
    def save_models(self):
        """Save trained models"""
        print("💾 Saving models...")
        
        os.makedirs("models", exist_ok=True)
        
        # Save individual models
        for name, model in self.models.items():
            joblib.dump(model, f"models/{name.lower()}_model.pkl")
        
        # Save ensemble model
        joblib.dump(self.ensemble_model, "models/ensemble_model.pkl")
        
        # Save scaler
        joblib.dump(self.scaler, "models/scaler.pkl")
        
        # Save feature importance
        importance_df = pd.DataFrame(self.feature_importance).fillna(0)
        importance_df.to_csv("outputs/feature_importance_advanced.csv")
        
        # Save model performance
        performance_df = pd.DataFrame({
            name: metrics for name, metrics in self.model_performance.items()
        }).T
        performance_df.to_csv("outputs/model_performance.csv")
        
        print("✅ Models saved successfully")
    
    def load_models(self):
        """Load pre-trained models"""
        print("📂 Loading models...")
        
        try:
            # Load ensemble model
            self.ensemble_model = joblib.load("models/ensemble_model.pkl")
            
            # Load scaler
            self.scaler = joblib.load("models/scaler.pkl")
            
            print("✅ Models loaded successfully")
            return True
        except FileNotFoundError:
            print("❌ Models not found. Please train models first.")
            return False
    
    def real_time_prediction(self, district_data):
        """Make real-time prediction for a single district"""
        if self.ensemble_model is None:
            if not self.load_models():
                return None
        
        # Prepare features
        features = list(district_data.keys())
        X = np.array([list(district_data.values())]).reshape(1, -1)
        X_scaled = self.scaler.transform(X)
        
        # Make prediction
        prediction = self.ensemble_model.predict(X_scaled)[0]
        probability = self.ensemble_model.predict_proba(X_scaled)[0][1]
        
        return {
            "prediction": int(prediction),
            "probability": float(probability),
            "risk_level": "High" if probability > 0.7 else "Medium" if probability > 0.3 else "Low",
            "confidence": "High" if abs(probability - 0.5) > 0.3 else "Medium"
        }

def main():
    """Main execution function"""
    print("🚀 Starting Advanced ML Pipeline...")
    
    # Load enhanced data
    try:
        df = pd.read_csv("outputs/enhanced_malnutrition_data.csv")
        print(f"✅ Loaded enhanced data: {len(df)} districts")
    except FileNotFoundError:
        print("❌ Enhanced data not found. Please run enhanced_data_processor.py first.")
        return
    
    # Initialize pipeline
    pipeline = AdvancedMLPipeline()
    
    # Prepare features
    X, y, features = pipeline.prepare_features(df)
    
    # Train models
    X_test, y_test = pipeline.train_individual_models(X, y, features)
    
    # Create ensemble
    pipeline.create_ensemble_model(X_test, y_test)
    
    # Generate predictions
    df_with_predictions = pipeline.generate_predictions(df, features)
    
    # Save everything
    pipeline.save_models()
    df_with_predictions.to_csv("outputs/predictions_advanced.csv", index=False)
    
    print("\n🎉 Advanced ML Pipeline completed successfully!")
    print(f"   Best model: {max(pipeline.model_performance.items(), key=lambda x: x[1]['auc'])[0]}")
    print(f"   Ensemble AUC: {pipeline.model_performance['Ensemble']['auc']:.3f}")

if __name__ == "__main__":
    main()
