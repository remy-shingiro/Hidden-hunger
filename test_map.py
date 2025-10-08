# test_map.py
# Test script to verify map functionality

import pandas as pd
import geopandas as gpd
import folium
import numpy as np

def test_map_functionality():
    """Test the map functionality without Streamlit"""
    print("Testing map functionality...")
    
    try:
        # Load data
        print("1. Loading data...")
        data = pd.read_csv("outputs/enhanced_malnutrition_data.csv")
        geo_data = gpd.read_file("data/rwanda_districts.geojson")
        
        # Clean data
        print("2. Cleaning data...")
        geo_data["district"] = geo_data["district"].str.strip().str.title()
        data["District"] = data["District"].str.strip().str.title()
        
        # Merge data
        print("3. Merging data...")
        geo_data = geo_data.merge(data, left_on="district", right_on="District", how="left")
        
        # Convert to strings for JSON serialization
        print("4. Converting data types...")
        for col in geo_data.columns:
            if col != "geometry":
                geo_data[col] = geo_data[col].astype(str)
        
        # Test color function
        print("5. Testing color function...")
        map_metric = "Malnutrition_Index"
        values = pd.to_numeric(geo_data[map_metric], errors='coerce').fillna(0)
        max_val = values.max()
        min_val = values.min()
        
        def get_color(val):
            if pd.isna(val) or val == "nan" or val == "":
                return "gray"
            try:
                num_val = float(val)
                normalized = (num_val - min_val) / (max_val - min_val) if max_val > min_val else 0
                if normalized > 0.7:
                    return "red"
                elif normalized > 0.4:
                    return "orange"
                else:
                    return "green"
            except (ValueError, TypeError):
                return "gray"
        
        # Test with sample values
        test_values = ["15.5", "25.3", "8.2", "nan", ""]
        for val in test_values:
            color = get_color(val)
            print(f"   Value: {val} -> Color: {color}")
        
        # Create map
        print("6. Creating map...")
        m = folium.Map(location=[-1.95, 30.06], zoom_start=8, tiles="cartodbpositron")
        
        # Test style function
        print("7. Testing style function...")
        style_function = lambda feature: {
            "fillColor": get_color(feature["properties"].get(map_metric)),
            "color": "black",
            "weight": 1,
            "fillOpacity": 0.7
        }
        
        # Test with first feature
        first_feature = geo_data.iloc[0]
        test_style = style_function({
            "properties": {
                map_metric: first_feature[map_metric]
            }
        })
        print(f"   Style function result: {test_style}")
        
        # Add GeoJSON
        print("8. Adding GeoJSON...")
        folium.GeoJson(
            geo_data,
            style_function=style_function,
            tooltip=folium.GeoJsonTooltip(
                fields=["District", map_metric, "Children_Under5"],
                aliases=["District", "Malnutrition Index", "Children Under 5"],
                localize=True
            )
        ).add_to(m)
        
        # Save map
        print("9. Saving map...")
        m.save("test_map.html")
        
        print("✅ Map test completed successfully!")
        print("   Map saved as test_map.html")
        print("   You can open it in a browser to verify functionality")
        
        return True
        
    except Exception as e:
        print(f"❌ Map test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_map_functionality()
    if success:
        print("\n🎉 Map functionality is working correctly!")
    else:
        print("\n❌ Map functionality needs fixing")
