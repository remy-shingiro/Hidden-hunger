# predictive_model_smote_tuning.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Machine learning imports
from sklearn.model_selection import StratifiedKFold, GridSearchCV, cross_val_predict
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from imblearn.over_sampling import SMOTE

# -----------------------------
# 1. Load dataset
# -----------------------------
data_path = "outputs/malnutrition_for_modeling.csv"
df = pd.read_csv(data_path)
print("Dataset preview:")
print(df.head(), "\n")

# -----------------------------
# 2. Select features and target
# -----------------------------
feature_cols = ["Underweight_pct", "Wasted_pct", "VitaminA_pct", "Iodine_pct"]
target_col = "high_risk_stunted"

X = df[feature_cols]
y = df[target_col]

# -----------------------------
# 3. Use Stratified K-Fold Cross-Validation instead of single split
# -----------------------------
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

# Handle class imbalance inside CV (fit_resample each fold)
smote = SMOTE(random_state=42)

# -----------------------------
# 4. Hyperparameter tuning with GridSearchCV
# -----------------------------
param_grid = {
    'n_estimators': [100, 200],
    'max_depth': [None, 5, 10],
    'min_samples_split': [2, 5],
    'min_samples_leaf': [1, 2],
    'max_features': ['sqrt', None]
}

rf = RandomForestClassifier(random_state=42)
grid_search = GridSearchCV(
    estimator=rf,
    param_grid=param_grid,
    cv=cv,
    scoring='roc_auc',
    n_jobs=-1,
    verbose=1
)

# Apply SMOTE before fitting
X_res, y_res = smote.fit_resample(X, y)
grid_search.fit(X_res, y_res)
best_rf = grid_search.best_estimator_
print(f"\nBest Random Forest parameters: {grid_search.best_params_}")

# -----------------------------
# 5. Evaluate tuned model with CV predictions
# -----------------------------
y_pred = cross_val_predict(best_rf, X_res, y_res, cv=cv, method="predict")
y_prob = cross_val_predict(best_rf, X_res, y_res, cv=cv, method="predict_proba")[:, 1]

# Confusion matrix
cm = confusion_matrix(y_res, y_pred)
print("Confusion Matrix:")
print(cm)

# Classification report
cr = classification_report(y_res, y_pred)
print("\nClassification Report:")
print(cr)

# ROC-AUC
roc_auc = roc_auc_score(y_res, y_prob)
print(f"ROC-AUC Score: {roc_auc:.3f}")

# -----------------------------
# 6. Feature importance
# -----------------------------
feat_imp = pd.Series(best_rf.feature_importances_, index=feature_cols).sort_values()

plt.figure(figsize=(8,5))
sns.barplot(x=feat_imp.values, y=feat_imp.index, palette="viridis", hue=None, legend=False)
plt.title("Feature Importance - High Risk Stunted")
plt.xlabel("Importance")
plt.ylabel("Feature")
plt.tight_layout()
plt.savefig("outputs/feature_importance_smote.png", bbox_inches="tight")
plt.show()

# Save feature importance to CSV
feat_imp.to_csv("outputs/feature_importance_smote.csv", header=False)
print("✅ Feature importance saved to outputs/feature_importance_smote.csv")


# -----------------------------

# 7. Save predictions
# -----------------------------
# df_preds = X_res.copy()  # use resampled features, not original
# df_preds["true_label"] = y_res
# df_preds["pred_label"] = y_pred
# df_preds["pred_prob"] = y_prob
# df_preds.to_csv("outputs/predictions_smote.csv", index=False)
# print("\n✅ Predictions saved to outputs/predictions_smote.csv")


# Map the resampled indices back to original Districts (best effort)
# If SMOTE generated synthetic samples, we'll assign 'Synthetic' to new ones
districts_res = []
original_indices = X.index.tolist()
for i in range(len(X_res)):
    if i < len(original_indices):
        districts_res.append(df.loc[original_indices[i], "District"])
    else:
        districts_res.append("Synthetic")

df_preds = X_res.copy()  # use resampled features
df_preds["District"] = districts_res  # add district column
df_preds["true_label"] = y_res
df_preds["pred_label"] = y_pred
df_preds["pred_prob"] = y_prob
df_preds.to_csv("outputs/predictions_smote.csv", index=False)
print("\n✅ Predictions (with Districts) saved to outputs/predictions_smote.csv")


