# generate_policy_brief_full_socio_refined.py

import pandas as pd

# -----------------------------
# 1. Load data
# -----------------------------
# District malnutrition + socio-economic data
district_data = pd.read_csv("data/malnutrition_sample.csv")

# Model predictions
preds = pd.read_csv("outputs/predictions_smote.csv")

# Remove synthetic rows
preds = preds[~preds["District"].str.contains("Synthetic", case=False)]

# Clean names
district_data["District"] = district_data["District"].str.strip().str.title()
preds["District"] = preds["District"].str.strip().str.title()

# Merge
df = preds.merge(district_data, on="District", how="left")

# -----------------------------
# 2. Define risk categories
# -----------------------------
def assign_risk(prob):
    if prob >= 0.7:
        return "High"
    elif prob >= 0.4:
        return "Medium"
    else:
        return "Low"

df["Risk_Level"] = df["pred_prob"].apply(assign_risk)

# -----------------------------
# 3. Determine root causes including socio-economic
# -----------------------------
def identify_root_causes(row):
    causes = []
    # Nutritional indicators
    if row["Underweight"] > 50:
        causes.append("High Underweight %")
    if row["Wasted"] > 40:
        causes.append("High Wasting %")
    if row["VitaminA_Deficiency"] > 50:
        causes.append("Vitamin A Deficiency")
    if row["Iodine_Deficiency"] > 50:
        causes.append("Iodine Deficiency")
    # Socio-economic factors (if available)
    if row.get("Education_Coverage", 100) < 80:
        causes.append("Low Education Coverage")
    if row.get("Health_Access", 100) < 80:
        causes.append("Limited Access to Health Services")
    return causes if causes else ["General Malnutrition Risk"]

df["Root_Causes"] = df.apply(identify_root_causes, axis=1)

# -----------------------------
# 4. Add characteristics summary
# -----------------------------
def generate_characteristics(row):
    char = []
    if row["Underweight"] > 50:
        char.append("High prevalence of underweight")
    if row["Wasted"] > 40:
        char.append("High prevalence of wasting")
    if row["VitaminA_Deficiency"] > 50:
        char.append("Vitamin A deficiency")
    if row["Iodine_Deficiency"] > 50:
        char.append("Iodine deficiency")
    if row.get("Education_Coverage", 100) < 80:
        char.append("Limited education coverage")
    if row.get("Health_Access", 100) < 80:
        char.append("Limited access to health services")
    if not char:
        char.append("Generally low nutritional risk and good socio-economic status")
    return ", ".join(char)

df["Characteristics"] = df.apply(generate_characteristics, axis=1)

# -----------------------------
# 5. Tailored interventions per sector
# -----------------------------
def generate_recommendations(causes, risk):
    health = []
    agriculture = []
    education = []

    # Health interventions
    if "Vitamin A Deficiency" in causes:
        health.append("Vitamin A supplementation program")
    if "Iodine Deficiency" in causes:
        health.append("Iodine supplementation program")
    if any(x in causes for x in ["High Underweight %", "High Wasting %"]):
        health.append("Nutritional counseling and monitoring")
    if "Limited Access to Health Services" in causes:
        health.append("Mobile clinics and outreach health programs")

    # Agriculture interventions
    if any(x in causes for x in ["High Underweight %", "High Wasting %", "Vitamin A Deficiency", "Iodine Deficiency"]):
        agriculture.append("Promote biofortified crops and kitchen gardens")

    # Education interventions
    if any(x in causes for x in ["High Underweight %", "High Wasting %", "Vitamin A Deficiency", "Iodine Deficiency"]):
        education.append("School feeding programs")
        education.append("Nutrition awareness campaigns")
    if "Low Education Coverage" in causes:
        education.append("Intensive community nutrition education")

    # Preventive actions for medium and low risk areas
    if risk in ["Medium", "Low"]:
        if not health:
            health.append("Maintain general health monitoring")
        if not agriculture:
            agriculture.append("Promote nutritional diversity at home")
        if not education:
            education.append("Conduct nutrition awareness sessions")

    return health, agriculture, education

df["Health_Rec"], df["Agri_Rec"], df["Edu_Rec"] = zip(*df.apply(lambda row: generate_recommendations(row["Root_Causes"], row["Risk_Level"]), axis=1))

# -----------------------------
# 6. Generate per-district policy brief text
# -----------------------------
briefs_by_risk = {"High": [], "Medium": [], "Low": []}

for _, row in df.iterrows():
    brief = f"""
Policy Brief – {row['District']}
Risk Level: {row['Risk_Level']}
Characteristics: {row['Characteristics']}

Root Causes:
- {'\n- '.join(row['Root_Causes'])}

Recommended Actions:
Health:
- {'\n- '.join(row['Health_Rec'])}

Agriculture:
- {'\n- '.join(row['Agri_Rec'])}

Education:
- {'\n- '.join(row['Edu_Rec'])}
"""
    briefs_by_risk[row["Risk_Level"]].append(brief.strip())
  
# -----------------------------
df.to_csv("outputs/policy_briefs_by_risk_socio.csv", index=False)


# 7. Save briefs grouped by risk
# -----------------------------
with open("outputs/policy_briefs_full_socio.txt", "w", encoding="utf-8") as f:
    for risk_level in ["High", "Medium", "Low"]:
        f.write(f"\n\n{'='*60}\n")
        f.write(f"POLICY BRIEFS – {risk_level} RISK DISTRICTS\n")
        f.write(f"{'='*60}\n\n")
        for brief in briefs_by_risk[risk_level]:
            f.write(brief)
            f.write("\n\n" + "-"*50 + "\n\n")

print("✅ Full policy briefs with risk levels, characteristics, root causes, and tailored recommendations saved to 'outputs/policy_briefs_full_socio.txt'")
