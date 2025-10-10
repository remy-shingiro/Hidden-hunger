import geopandas as gpd
import pandas as pd
import folium

# -----------------------------
# 1. Load Malnutrition Data
# -----------------------------
malnutrition_data = pd.read_csv("data/malnutrition_sample.csv")
print("Malnutrition Data Preview:")
print(malnutrition_data.head())

# -----------------------------
# 2. Load Rwanda Shapefile
# -----------------------------
shapefile_path = "data/rwanda_districts_shapefile/District_Boundaries.shp"
districts = gpd.read_file(shapefile_path)
print("\nShapefile Columns:", districts.columns)

# -----------------------------
# 3. Standardize Names
# -----------------------------
# Rename shapefile column to match CSV naming
districts = districts.rename(columns={"district": "District"})

# Convert both CSV and shapefile District names to lowercase + strip spaces
districts["District"] = districts["District"].str.strip().str.lower()
malnutrition_data["District"] = malnutrition_data["District"].str.strip().str.lower()

# -----------------------------
# 3b. Convert Non-geometry Columns to Serializable
# -----------------------------
for col in districts.columns:
    if col != "geometry" and not pd.api.types.is_numeric_dtype(districts[col]):
        districts[col] = districts[col].astype(str)

# -----------------------------
# 4. Merge Data
# -----------------------------
districts = districts.merge(malnutrition_data, on="District", how="left")
print("\nMerged Data Preview:")
print(districts[["District", "Children_Under5", "Stunted"]].head())

# -----------------------------
# 5. Create Interactive Map
# -----------------------------
# Center the map roughly on Rwanda
m = folium.Map(location=[-1.94, 29.87], zoom_start=8)

# -----------------------------
# 6. Add Choropleth Layer for Stunting
# -----------------------------
folium.Choropleth(
    geo_data=districts,
    name="Stunting",
    data=districts,
    columns=["District", "Stunted"],
    key_on="feature.properties.District",
    fill_color="YlOrRd",
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name="Stunted Children (under 5)"
).add_to(m)

# -----------------------------
# 7. Add Hover Tooltips
# -----------------------------
folium.GeoJson(
    districts,
    style_function=lambda x: {"fillColor": "transparent", "color": "black", "weight": 0.5},
    tooltip=folium.GeoJsonTooltip(
        fields=["District", "Children_Under5", "Stunted", "Underweight", "Wasted", "VitaminA_Deficiency", "Iodine_Deficiency"],
        aliases=["District", "Children Under 5", "Stunted", "Underweight", "Wasted", "Vitamin A Deficiency", "Iodine Deficiency"],
        localize=True
    )
).add_to(m)

# -----------------------------
# 8. Optional: Add CSV Point Markers
# -----------------------------
for _, row in malnutrition_data.iterrows():
    popup_text = f"""
    <b>{row['District'].title()}</b><br>
    Children Under 5: {row['Children_Under5']}<br>
    Stunted: {row['Stunted']}<br>
    Underweight: {row['Underweight']}<br>
    Wasted: {row['Wasted']}<br>
    Vitamin A Deficiency: {row['VitaminA_Deficiency']}<br>
    Iodine Deficiency: {row['Iodine_Deficiency']}
    """
    folium.CircleMarker(
        location=[row['Latitude'], row['Longitude']],
        radius=6,
        color="blue",
        fill=True,
        fill_opacity=0.7,
        popup=popup_text
    ).add_to(m)

# -----------------------------
# 9. Save Map
# -----------------------------
m.save("rwanda_malnutrition_map.html")
print("\n✅ Map has been saved to 'rwanda_malnutrition_map.html'. Open it in a browser.")




