
# exploratory_analysis.py
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd

# -----------------------------
# Make output folder
# -----------------------------
OUTDIR = "outputs"
os.makedirs(OUTDIR, exist_ok=True)

# -----------------------------
# 1. Load data
# -----------------------------
csv_path = "data/malnutrition_sample.csv"
shapefile_path = "data/rwanda_districts_shapefile/District_Boundaries.shp"

# Safe CSV load
try:
    df = pd.read_csv(csv_path)
    print("Loaded CSV:", csv_path)
    print(df.head(), "\n")
except FileNotFoundError:
    raise FileNotFoundError(f"CSV file not found at {csv_path}")

# Quick data info
print("=== CSV info ===")
print(df.info(), "\n")
print("=== Summary statistics ===")
print(df.describe(include="all").T, "\n")

# -----------------------------
# 2. Basic cleaning + safe numeric conversion
# -----------------------------
df["District"] = df["District"].astype(str).str.strip().str.lower()

num_cols = ["Children_Under5", "Stunted", "Underweight", "Wasted",
            "VitaminA_Deficiency", "Iodine_Deficiency", "Latitude", "Longitude"]
for c in num_cols:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")

missing = df.isna().sum()
print("=== Missing values per column ===")
print(missing)
missing.to_csv(os.path.join(OUTDIR, "missing_counts.csv"))

# -----------------------------
# 3. Create percentage columns (robust)
# -----------------------------
children = df["Children_Under5"].fillna(0)

# Core indicators
df["Stunted_pct"] = np.where(children > 0, (df["Stunted"] / children) * 100, np.nan)
df["Underweight_pct"] = np.where(children > 0, (df["Underweight"] / children) * 100, np.nan)
df["Wasted_pct"] = np.where(children > 0, (df["Wasted"] / children) * 100, np.nan)
df["VitaminA_pct"] = np.where(children > 0, (df["VitaminA_Deficiency"] / children) * 100, np.nan)
df["Iodine_pct"]   = np.where(children > 0, (df["Iodine_Deficiency"] / children) * 100, np.nan)

# Optional indicators: check existence before calculation
for col in ["VitaminA_Deficiency", "Iodine_Deficiency"]:
    if col in df.columns:
        df[col + "_pct"] = np.where(children > 0, (df[col] / children) * 100, np.nan)

# Round for readability
pct_cols = [c for c in df.columns if "_pct" in c]
df[pct_cols] = df[pct_cols].round(2)
df.to_csv(os.path.join(OUTDIR, "malnutrition_with_pct.csv"), index=False)

# -----------------------------
# 3b. Advanced feature engineering (per_1000 and micronutrient score)
# -----------------------------
df["stunted_per_1000"] = np.where(children > 0, df["Stunted"] / children * 1000, np.nan)
df["underweight_per_1000"] = np.where(children > 0, df["Underweight"] / children * 1000, np.nan)
df["wasted_per_1000"] = np.where(children > 0, df["Wasted"] / children * 1000, np.nan)

# Micronutrient deficiency index
if "VitaminA_pct" in df.columns and "Iodine_pct" in df.columns:
    df["micronutrient_deficiency_score"] = df["VitaminA_pct"] + df["Iodine_pct"]

# -----------------------------
# 4. Quick univariate plots
# -----------------------------
plt.figure(figsize=(8,5))
sns.histplot(df["Stunted_pct"].dropna(), bins=12, kde=True)
plt.title("Distribution of Stunted % (children under 5)")
plt.xlabel("Stunted (%)")
plt.tight_layout()
plt.savefig(os.path.join(OUTDIR, "hist_stunted_pct.png"), bbox_inches="tight")
plt.close()

plt.figure(figsize=(8,5))
sns.boxplot(x=df["Stunted_pct"].dropna())
plt.title("Boxplot - Stunted %")
plt.tight_layout()
plt.savefig(os.path.join(OUTDIR, "box_stunted_pct.png"), bbox_inches="tight")
plt.close()

# Histograms for remaining percentage columns
for c in pct_cols:
    plt.figure(figsize=(8,4))
    sns.histplot(df[c].dropna(), bins=12, kde=True)
    plt.title(f"Distribution of {c}")
    plt.xlabel(c)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTDIR, f"hist_{c}.png"), bbox_inches="tight")
    plt.close()

# -----------------------------
# 5. Correlation analysis
# -----------------------------
corr_cols = ["Children_Under5", "Stunted", "Underweight", "Wasted"] + pct_cols
corr_df = df[corr_cols].copy()
corr = corr_df.corr(method="pearson")
plt.figure(figsize=(10,8))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdYlGn_r", vmin=-1, vmax=1)
plt.title("Correlation matrix (Pearson)")
plt.tight_layout()
plt.savefig(os.path.join(OUTDIR, "correlation_matrix.png"), bbox_inches="tight")
plt.close()
corr.to_csv(os.path.join(OUTDIR, "correlation_matrix.csv"))

# -----------------------------
# 6. Scatter & relationships
# -----------------------------
plt.figure(figsize=(7,6))
sns.scatterplot(data=df, x="Stunted_pct", y="Underweight_pct")
plt.title("Stunted % vs Underweight %")
plt.tight_layout()
plt.savefig(os.path.join(OUTDIR, "scatter_stunted_vs_underweight.png"), bbox_inches="tight")
plt.close()

# -----------------------------
# 7. Create a simple 'risk' target
# -----------------------------
median_val = df["Stunted_pct"].median(skipna=True)
q75 = df["Stunted_pct"].quantile(0.75)
print(f"Stunted_pct median = {median_val:.2f}, 75th percentile = {q75:.2f}")

df["high_risk_stunted"] = np.where(df["Stunted_pct"] > q75, 1, 0)
print("High risk counts (stunted):\n", df["high_risk_stunted"].value_counts())
df.to_csv(os.path.join(OUTDIR, "malnutrition_for_modeling.csv"), index=False)

# -----------------------------
# 8. Class balance check
# -----------------------------
balance = df["high_risk_stunted"].value_counts(normalize=True)
print("Class balance for target (proportion):")
print(balance)
balance.to_csv(os.path.join(OUTDIR, "class_balance.csv"))

# -----------------------------
# 9. Quick spatial check (robust merging)
# -----------------------------
try:
    gdf = gpd.read_file(shapefile_path)
except FileNotFoundError:
    raise FileNotFoundError(f"Shapefile not found at {shapefile_path}")

gdf = gdf.rename(columns={"district": "District"})
gdf["District"] = gdf["District"].str.strip().str.lower()

# Check unmatched districts
unmatched = set(df["District"]) - set(gdf["District"])
if unmatched:
    print("Warning: districts not found in shapefile:", unmatched)

# Merge
gdf = gdf.merge(df, on="District", how="left")

# Convert timestamps to str if any
for c in gdf.columns:
    if c != "geometry" and pd.api.types.is_datetime64_any_dtype(gdf[c]):
        gdf[c] = gdf[c].astype(str)

gdf.to_file(os.path.join(OUTDIR, "districts_with_data.geojson"), driver="GeoJSON")

# -----------------------------
# 9b. Choropleth maps (new)
# -----------------------------
# Map stunted percentage
plt.figure(figsize=(10,10))
gdf.plot(column="Stunted_pct", cmap="Reds", legend=True, edgecolor="black")
plt.title("Stunted % by District")
plt.axis("off")
plt.savefig(os.path.join(OUTDIR, "map_stunted_pct.png"), bbox_inches="tight")
plt.close()

# Map high-risk stunted districts
plt.figure(figsize=(10,10))
gdf.plot(column="high_risk_stunted", cmap="Reds", legend=True, edgecolor="black")
plt.title("High Risk Stunted Districts")
plt.axis("off")
plt.savefig(os.path.join(OUTDIR, "map_high_risk_stunted.png"), bbox_inches="tight")
plt.close()

# Optional: top 5 districts by stunted %
print("Top 5 districts by stunted %:")
print(df.sort_values("Stunted_pct", ascending=False)[["District", "Stunted_pct"]].head())

# -----------------------------
# 10. Recommendations from EDA
# -----------------------------
print("\n=== EDA recommendations / things to inspect ===")
print("""
1) Look at distributions: if Stunted_pct (or others) is highly skewed, consider log transform
   for modeling or use tree models (which handle skewness).
2) If Stunted correlates very strongly with Underweight/Wasted, you may drop one to reduce
   multicollinearity or engineer a combined score.
3) If high_risk class is imbalanced (very small), plan for stratified split or resampling (SMOTE).
4) Missing values: decide per-column imputation strategy:
   - small % missing -> median impute
   - systematic missingness -> investigate data source
5) Feature engineering ideas: ratios (e.g., stunted_per_1000 = stunted/children*1000),
   micronutrient score (VitaminA + Iodine), external socio-economic features,
   seasonality or location features (province, elevation), access to health facilities.
6) Prepare tidy dataset saved to outputs/malnutrition_for_modeling.csv for modeling stage.
""")

print("\nPlots and CSVs were saved to the 'outputs/' folder.")
