# # dashboard.py

# import streamlit as st
# import pandas as pd
# import geopandas as gpd
# import folium
# from streamlit_folium import st_folium
# import plotly.express as px
# import matplotlib.pyplot as plt
# import ast

# # -----------------------------
# # 1. Load preprocessed data
# # -----------------------------
# df = pd.read_csv("outputs/policy_briefs_by_risk_socio.csv")

# # -----------------------------
# # # Utility: safe parser for list-like strings
# # # -----------------------------
# # def safe_parse_list(val):
# #     if pd.isna(val):
# #         return []
# #     try:
# #         cleaned = val.strip()
# #         if not cleaned.startswith("["):
# #             cleaned = "[" + cleaned + "]"
# #         # Add quotes around items if they are missing
# #         cleaned = cleaned.replace(", ", '","').replace("[", '["').replace("]", '"]')
# #         return ast.literal_eval(cleaned)
# #     except Exception:
# #         return [val]
    

#     # -----------------------------
# # Utility: safe parser for list-like strings
# # -----------------------------
# def safe_parse_list(val):
#     # If already a list, return as-is
#     if isinstance(val, list):
#         return val
#     # If scalar NaN, return empty list
#     if pd.isna(val):
#         return []
#     try:
#         cleaned = str(val).strip()
#         if not cleaned.startswith("["):
#             cleaned = "[" + cleaned + "]"
#         # Add quotes around items if missing
#         cleaned = cleaned.replace(", ", '","').replace("[", '["').replace("]", '"]')
#         return ast.literal_eval(cleaned)
#     except Exception:
#         # fallback: return original value as single-item list
#         return [str(val)]



# # Apply cleaning
# df["Root_Causes"] = df["Root_Causes"].astype(str)
# df["Health_Rec"] = df["Health_Rec"].apply(safe_parse_list)
# df["Agri_Rec"] = df["Agri_Rec"].apply(safe_parse_list)
# df["Edu_Rec"] = df["Edu_Rec"].apply(safe_parse_list)

# # -----------------------------
# # 2. Streamlit sidebar filters
# # -----------------------------
# st.sidebar.title("Filters")
# risk_levels = st.sidebar.multiselect(
#     "Select Risk Levels",
#     options=df["Risk_Level"].unique(),
#     default=df["Risk_Level"].unique()
# )

# province_filter = st.sidebar.text_input("Filter by Province (optional)")

# # Apply filters
# df_filtered = df[df["Risk_Level"].isin(risk_levels)]

# # -----------------------------
# # 3. Title
# # -----------------------------
# st.title("🌍 Rwanda Malnutrition Risk Dashboard")

# st.markdown("""
# This dashboard provides insights into **malnutrition risks across Rwandan districts**,
# highlighting **root causes** and **tailored interventions** in **health, agriculture, and education**.
# """)

# # -----------------------------
# # 4. Load Rwanda shapefile
# # -----------------------------
# gdf = gpd.read_file("data/rwanda_districts.geojson")


# # Drop non-serializable timestamp columns
# for col in gdf.columns:
#     if "date" in col.lower():
#         gdf = gdf.drop(columns=[col])

# # Standardize names
# gdf["district"] = gdf["district"].str.strip().str.title()
# df_filtered["District"] = df_filtered["District"].str.strip().str.title()

# # Merge shapefile with data
# gdf = gdf.merge(df_filtered, left_on="district", right_on="District", how="left")

# # -----------------------------
# # 5. Folium Map (Rwanda only)
# # -----------------------------
# m = folium.Map(location=[-1.95, 30.06], zoom_start=8, tiles="cartodbpositron")

# # Define colors for risk levels
# color_map = {"High": "red", "Medium": "orange", "Low": "green"}

# def style_function(feature):
#     risk = feature["properties"]["Risk_Level"]
#     return {
#         "fillOpacity": 0.6,
#         "weight": 0.5,
#         "fillColor": color_map.get(risk, "gray"),
#         "color": "black"
#     }

# # Popup template
# def make_popup(props):
#     district = props["district"]
#     risk = props["Risk_Level"]
#     causes = props["Root_Causes"]

#     health_recs = "<br>".join([f"- {rec}" for rec in safe_parse_list(props["Health_Rec"])])
#     agri_recs = "<br>".join([f"- {rec}" for rec in safe_parse_list(props["Agri_Rec"])])
#     edu_recs = "<br>".join([f"- {rec}" for rec in safe_parse_list(props["Edu_Rec"])])

#     return f"""
#     <div style="font-size:14px;">
#         <b>District:</b> {district}<br>
#         <b>Risk Level:</b> {risk}<br><br>
#         <b>Root Causes:</b><br> {causes}<br><br>
#         <b>Health Recommendations:</b><br>{health_recs}<br><br>
#         <b>Agriculture Recommendations:</b><br>{agri_recs}<br><br>
#         <b>Education Recommendations:</b><br>{edu_recs}
#     </div>
#     """

# folium.GeoJson(
#     gdf,
#     name="Rwanda Districts",
#     style_function=style_function,
#     highlight_function=lambda x: {"weight": 3, "color": "blue"},
#     tooltip=folium.GeoJsonTooltip(fields=["district", "Risk_Level"], aliases=["District:", "Risk Level:"]),
#     popup=folium.GeoJsonPopup(fields=["district", "Risk_Level", "Root_Causes", "Health_Rec", "Agri_Rec", "Edu_Rec"],
#                               labels=False,
#                               localize=True,
#                               parse_html=True,
#                               style="background-color: white;"),
# ).add_to(m)

# # Add legend
# legend_html = """
# <div style="position: fixed; bottom: 50px; left: 50px; width: 150px; height: 120px; 
#      border:2px solid grey; z-index:9999; font-size:14px; background:white; padding:10px;">
#      <b>Risk Levels</b><br>
#      <i style="background:red;width:10px;height:10px;display:inline-block;margin-right:5px;"></i> High<br>
#      <i style="background:orange;width:10px;height:10px;display:inline-block;margin-right:5px;"></i> Medium<br>
#      <i style="background:green;width:10px;height:10px;display:inline-block;margin-right:5px;"></i> Low
# </div>
# """
# m.get_root().html.add_child(folium.Element(legend_html))

# st.subheader("🗺️ Rwanda Districts Map")
# st_folium(m, width=1000, height=700)

# # -----------------------------
# # 6. Top 5 High-Risk Districts
# # -----------------------------
# st.subheader("🔥 Top 5 High-Risk Districts")
# top5 = df_filtered[df_filtered["Risk_Level"] == "High"].sort_values(by="pred_prob", ascending=False).head(5)

# for _, row in top5.iterrows():
#     st.markdown(f"### {row['District']} (Risk: {row['Risk_Level']})")
#     st.markdown(f"**Root Causes:** {row['Root_Causes']}")
#     st.markdown("**Health Recommendations:**")
#     for rec in safe_parse_list(row["Health_Rec"]):
#         st.markdown(f"- {rec}")
#     st.markdown("**Agriculture Recommendations:**")
#     for rec in safe_parse_list(row["Agri_Rec"]):
#         st.markdown(f"- {rec}")
#     st.markdown("**Education Recommendations:**")
#     for rec in safe_parse_list(row["Edu_Rec"]):
#         st.markdown(f"- {rec}")
#     st.markdown("---")

# # -----------------------------
# # 7. Feature Importance Plot
# # -----------------------------
# st.subheader("📊 Feature Importance (Random Forest Model)")

# # Read CSV without setting index_col
# feat_imp = pd.read_csv("outputs/feature_importance_smote.csv", header=None, names=["Feature", "Importance"])

# # Sort by importance
# feat_imp = feat_imp.sort_values(by="Importance", ascending=True)

# # Plotly horizontal bar
# fig = px.bar(
#     feat_imp,
#     x="Importance",
#     y="Feature",
#     orientation="h",
#     title="Feature Importance",
#     color="Importance",
#     color_continuous_scale="Viridis"
# )

# st.plotly_chart(fig, use_container_width=True)


# # -----------------------------
# # End
# # -----------------------------
# st.success("✅ Dashboard loaded successfully with refined design and safe list parsing.")






# # dashboard.py

# import streamlit as st
# import pandas as pd
# import geopandas as gpd
# import folium
# from streamlit_folium import st_folium
# import plotly.express as px
# import ast

# # -----------------------------
# # Page config for wide layout
# # -----------------------------
# st.set_page_config(page_title="Rwanda Malnutrition Risk Dashboard", layout="wide")

# # -----------------------------
# # 1. Load preprocessed data
# # -----------------------------
# df = pd.read_csv("outputs/policy_briefs_by_risk_socio.csv")

# # -----------------------------
# # Utility: safe parser for list-like strings
# # -----------------------------
# def safe_parse_list(val):
#     if isinstance(val, list):
#         return val
#     if pd.isna(val):
#         return []
#     try:
#         cleaned = str(val).strip()
#         if not cleaned.startswith("["):
#             cleaned = "[" + cleaned + "]"
#         cleaned = cleaned.replace(", ", '","').replace("[", '["').replace("]", '"]')
#         return ast.literal_eval(cleaned)
#     except Exception:
#         return [str(val)]

# # Clean lists
# df["Root_Causes"] = df["Root_Causes"].astype(str)
# df["Health_Rec"] = df["Health_Rec"].apply(safe_parse_list)
# df["Agri_Rec"] = df["Agri_Rec"].apply(safe_parse_list)
# df["Edu_Rec"] = df["Edu_Rec"].apply(safe_parse_list)

# # -----------------------------
# # 2. Sidebar filters
# # -----------------------------
# st.sidebar.title("Filters")
# risk_levels = st.sidebar.multiselect(
#     "Select Risk Levels",
#     options=df["Risk_Level"].unique(),
#     default=df["Risk_Level"].unique()
# )
# province_filter = st.sidebar.text_input("Filter by Province (optional)")
# df_filtered = df[df["Risk_Level"].isin(risk_levels)]

# # -----------------------------
# # 3. Title
# # -----------------------------
# st.title("🌍 Rwanda Malnutrition Risk Dashboard")
# st.markdown("""
# This dashboard provides insights into **malnutrition risks across Rwandan districts**,
# highlighting **root causes** and **tailored interventions** in **health, agriculture, and education**.
# """)

# # -----------------------------
# # 4. Load Rwanda shapefile
# # -----------------------------
# gdf = gpd.read_file("data/rwanda_districts.geojson")

# # Drop timestamp columns
# for col in gdf.columns:
#     if "date" in col.lower():
#         gdf = gdf.drop(columns=[col])

# # Standardize names and merge
# gdf["district"] = gdf["district"].str.strip().str.title()
# df_filtered["District"] = df_filtered["District"].str.strip().str.title()
# gdf = gdf.merge(df_filtered, left_on="district", right_on="District", how="left")

# # -----------------------------
# # 5. Folium Map
# # -----------------------------
# m = folium.Map(location=[-1.95, 30.06], zoom_start=8, tiles="cartodbpositron")
# color_map = {"High": "red", "Medium": "orange", "Low": "green"}

# def style_function(feature):
#     risk = feature["properties"]["Risk_Level"]
#     return {
#         "fillOpacity": 0.6,
#         "weight": 0.5,
#         "fillColor": color_map.get(risk, "gray"),
#         "color": "black"
#     }

# folium.GeoJson(
#     gdf,
#     name="Rwanda Districts",
#     style_function=style_function,
#     highlight_function=lambda x: {"weight": 3, "color": "blue"},
#     tooltip=folium.GeoJsonTooltip(fields=["district", "Risk_Level"], aliases=["District:", "Risk Level:"])
# ).add_to(m)

# # Add legend
# legend_html = """
# <div style="position: fixed; bottom: 50px; left: 50px; width: 150px; height: 120px; 
#      border:2px solid grey; z-index:9999; font-size:14px; background:white; padding:10px;">
#      <b>Risk Levels</b><br>
#      <i style="background:red;width:10px;height:10px;display:inline-block;margin-right:5px;"></i> High<br>
#      <i style="background:orange;width:10px;height:10px;display:inline-block;margin-right:5px;"></i> Medium<br>
#      <i style="background:green;width:10px;height:10px;display:inline-block;margin-right:5px;"></i> Low
# </div>
# """
# m.get_root().html.add_child(folium.Element(legend_html))

# # -----------------------------
# # 6. Layout: Map + Top districts
# # -----------------------------
# col1, col2 = st.columns([2, 1])

# with col1:
#     st.subheader("🗺️ Rwanda Districts Map")
#     st_folium(m, width=800, height=700)

# with col2:
#     st.subheader("🔥 Top 5 High-Risk Districts")
#     top5 = df_filtered[df_filtered["Risk_Level"] == "High"].sort_values(by="pred_prob", ascending=False).head(5)
    
#     for _, row in top5.iterrows():
#         st.markdown(f"### {row['District']} (Risk: {row['Risk_Level']})")
#         st.markdown(f"**Root Causes:** {row['Root_Causes']}")
#         with st.expander("Health Recommendations 🏥"):
#             for rec in safe_parse_list(row["Health_Rec"]):
#                 st.markdown(f"- {rec}")
#         with st.expander("Agriculture Recommendations 🌾"):
#             for rec in safe_parse_list(row["Agri_Rec"]):
#                 st.markdown(f"- {rec}")
#         with st.expander("Education Recommendations 🎓"):
#             for rec in safe_parse_list(row["Edu_Rec"]):
#                 st.markdown(f"- {rec}")
#         st.markdown("---")

# # -----------------------------
# # 7. Feature Importance
# # -----------------------------
# st.subheader("📊 Feature Importance (Random Forest Model)")
# feat_imp = pd.read_csv("outputs/feature_importance_smote.csv", header=None, names=["Feature", "Importance"])
# feat_imp = feat_imp.sort_values(by="Importance", ascending=True)
# top_features = feat_imp.tail(10)  # show only top 10
# fig = px.bar(
#     top_features,
#     x="Importance",
#     y="Feature",
#     orientation="h",
#     title="Top 10 Feature Importance",
#     color="Importance",
#     color_continuous_scale="Viridis"
# )
# st.plotly_chart(fig, use_container_width=True)

# # -----------------------------
# # End
# # -----------------------------
# st.success("✅ Dashboard loaded successfully with improved UI/UX.")





# # dashboard.py

# import streamlit as st
# import pandas as pd
# import geopandas as gpd
# import folium
# from streamlit_folium import st_folium
# import plotly.express as px
# import ast

# # -----------------------------
# # Page config
# # -----------------------------
# st.set_page_config(page_title="Rwanda Malnutrition Risk Dashboard", layout="wide")

# # -----------------------------
# # 1. Load preprocessed data
# # -----------------------------
# df = pd.read_csv("outputs/policy_briefs_by_risk_socio.csv")

# # -----------------------------
# # 2. Safe parser for list-like strings
# # -----------------------------
# def safe_parse_list(val):
#     if isinstance(val, list):
#         return val
#     if pd.isna(val):
#         return []
#     try:
#         cleaned = str(val).strip()
#         if not cleaned.startswith("["):
#             cleaned = "[" + cleaned + "]"
#         cleaned = cleaned.replace(", ", '","').replace("[", '["').replace("]", '"]')
#         return ast.literal_eval(cleaned)
#     except Exception:
#         return [str(val)]

# # Apply parsing
# df["Root_Causes"] = df["Root_Causes"].astype(str)
# df["Health_Rec"] = df["Health_Rec"].apply(safe_parse_list)
# df["Agri_Rec"] = df["Agri_Rec"].apply(safe_parse_list)
# df["Edu_Rec"] = df["Edu_Rec"].apply(safe_parse_list)

# # -----------------------------
# # 3. Sidebar filters
# # -----------------------------
# st.sidebar.title("Filters")
# risk_levels = st.sidebar.multiselect(
#     "Select Risk Levels",
#     options=df["Risk_Level"].unique(),
#     default=df["Risk_Level"].unique()
# )
# province_filter = st.sidebar.text_input("Filter by Province (optional)")
# df_filtered = df[df["Risk_Level"].isin(risk_levels)]

# # -----------------------------
# # 4. Title
# # -----------------------------
# st.title("🌍 Rwanda Malnutrition Risk Dashboard")
# st.markdown("""
# This dashboard provides insights into **malnutrition risks across Rwandan districts**,
# highlighting **root causes** and **tailored interventions** in **health, agriculture, and education**.
# """)

# # -----------------------------
# # 5. Load Rwanda shapefile
# # -----------------------------
# gdf = gpd.read_file("data/rwanda_districts.geojson")
# for col in gdf.columns:
#     if "date" in col.lower():
#         gdf = gdf.drop(columns=[col])

# gdf["district"] = gdf["district"].str.strip().str.title()
# df_filtered["District"] = df_filtered["District"].str.strip().str.title()
# gdf = gdf.merge(df_filtered, left_on="district", right_on="District", how="left")

# # -----------------------------
# # 6. Interactive map setup
# # -----------------------------
# m = folium.Map(location=[-1.95, 30.06], zoom_start=8, tiles="cartodbpositron")
# color_map = {"High": "red", "Medium": "orange", "Low": "green"}

# # Initialize session state for selected district
# if "selected_district" not in st.session_state:
#     st.session_state.selected_district = None

# def style_function(feature):
#     risk = feature["properties"]["Risk_Level"]
#     return {
#         "fillOpacity": 0.6,
#         "weight": 0.5,
#         "fillColor": color_map.get(risk, "gray"),
#         "color": "black"
#     }

# def on_click(feature):
#     district_name = feature["properties"]["district"]
#     st.session_state.selected_district = district_name

# # Add GeoJson
# folium.GeoJson(
#     gdf,
#     name="Rwanda Districts",
#     style_function=style_function,
#     highlight_function=lambda x: {"weight": 3, "color": "blue"},
#     tooltip=folium.GeoJsonTooltip(fields=["district", "Risk_Level"], aliases=["District:", "Risk Level:"]),
#     # We'll handle clicks via st_folium later
# ).add_to(m)

# legend_html = """
# <div style="position: fixed; bottom: 50px; left: 50px; width: 150px; height: 120px; 
#      border:2px solid grey; z-index:9999; font-size:14px; background:white; padding:10px;">
#      <b>Risk Levels</b><br>
#      <i style="background:red;width:10px;height:10px;display:inline-block;margin-right:5px;"></i> High<br>
#      <i style="background:orange;width:10px;height:10px;display:inline-block;margin-right:5px;"></i> Medium<br>
#      <i style="background:green;width:10px;height:10px;display:inline-block;margin-right:5px;"></i> Low
# </div>
# """
# m.get_root().html.add_child(folium.Element(legend_html))

# # -----------------------------
# # 7. Layout: Map + District Info
# # -----------------------------
# col1, col2 = st.columns([2, 1])

# with col1:
#     st.subheader("🗺️ Rwanda Districts Map")
#     map_data = st_folium(m, width=800, height=700)

#     # Capture clicked district
#     if map_data["last_active_drawing"]:
#         clicked_props = map_data["last_active_drawing"]["properties"]
#         st.session_state.selected_district = clicked_props["district"]

# with col2:
#     if st.session_state.selected_district:
#         district_data = df_filtered[df_filtered["District"] == st.session_state.selected_district]
#         if not district_data.empty:
#             row = district_data.iloc[0]
#             st.markdown(f"### {row['District']} (Risk: {row['Risk_Level']})")
#             st.markdown(f"**Root Causes:** {row['Root_Causes']}")
#             with st.expander("Health Recommendations 🏥"):
#                 for rec in safe_parse_list(row["Health_Rec"]):
#                     st.markdown(f"- {rec}")
#             with st.expander("Agriculture Recommendations 🌾"):
#                 for rec in safe_parse_list(row["Agri_Rec"]):
#                     st.markdown(f"- {rec}")
#             with st.expander("Education Recommendations 🎓"):
#                 for rec in safe_parse_list(row["Edu_Rec"]):
#                     st.markdown(f"- {rec}")
#         else:
#             st.info("Click on a district to see recommendations.")
#     else:
#         st.info("Click on a district to see recommendations.")

# # -----------------------------
# # 8. Feature Importance
# # -----------------------------
# st.subheader("📊 Feature Importance (Random Forest Model)")
# feat_imp = pd.read_csv("outputs/feature_importance_smote.csv", header=None, names=["Feature", "Importance"])
# feat_imp = feat_imp.sort_values(by="Importance", ascending=True)
# top_features = feat_imp.tail(10)
# fig = px.bar(
#     top_features,
#     x="Importance",
#     y="Feature",
#     orientation="h",
#     title="Top 10 Feature Importance",
#     color="Importance",
#     color_continuous_scale="Viridis"
# )
# st.plotly_chart(fig, use_container_width=True)

# # -----------------------------
# # End
# # -----------------------------
# st.success("✅ Dashboard loaded successfully with interactive map selection!")





# # dashboard.py

# import streamlit as st
# import pandas as pd
# import geopandas as gpd
# import folium
# from streamlit_folium import st_folium
# import plotly.express as px
# import ast
# from datetime import datetime
# import numpy as np

# # -----------------------------
# # Page config (Must be the very first Streamlit command)
# # -----------------------------
# st.set_page_config(page_title="NISR 2025 Big Data Hackathon", layout="wide")

# # -----------------------------
# # Custom CSS for the visual style (Card-like containers)
# # -----------------------------
# st.markdown(
#     """
#     <style>
#     /* Hide the Streamlit Header and Footer */
#     #MainMenu {visibility: hidden;}
#     footer {visibility: hidden;}
    
#     /* Custom container styling to mimic Figma cards */
#     .stContainer {
#         border: 1px solid #e6e6e6;
#         border-radius: 10px;
#         padding: 20px;
#         box-shadow: 2px 2px 8px rgba(0,0,0,0.05);
#         margin-bottom: 20px;
#     }
    
#     /* Custom Header/Nav Bar Styling */
#     .header-bar {
#         display: flex;
#         justify-content: space-between;
#         align-items: center;
#         padding: 10px 0;
#         margin-bottom: 20px;
#         border-bottom: 1px solid #f0f2f6;
#     }
#     .header-left {
#         font-size: 20px;
#         font-weight: 700;
#         color: #1f3d7a;
#     }
#     .header-right a {
#         color: #1f3d7a;
#         margin-left: 15px;
#         text-decoration: none;
#     }
#     .user-profile {
#         margin-left: 20px;
#         display: flex;
#         align-items: center;
#     }
#     .user-profile span {
#         margin-right: 5px;
#     }
    
#     /* Override for map height within container */
#     .stContainer iframe {
#         min-height: 450px !important; 
#     }
    
#     /* Custom styling for the main title and sub-title */
#     h1 {
#         padding-top: 0 !important;
#     }
#     h3 {
#         color: #1f3d7a;
#     }
#     </style>
#     """,
#     unsafe_allow_html=True,
# )

# # -----------------------------
# # 0. Custom Header Bar (Cloning the Image's Top Section)
# # -----------------------------

# # Use Streamlit columns to layout the title, nav links, and user icon
# col_h1, col_h2, col_h3 = st.columns([4, 2, 1])

# with col_h1:
#     st.markdown(f'<div class="header-left">NISR 2025 Big Data Hackathon</div>', unsafe_allow_html=True)
# with col_h2:
#     st.markdown(
#         """
#         <div class="header-right">
#             <a href="#">Home</a>
#             <a href="#">Challenges</a>
#             <a href="#">Solutions</a>
#         </div>
#         """, unsafe_allow_html=True
#     )
# with col_h3:
#     st.markdown('<div class="user-profile">👤 Team Uhuru 🇷🇼</div>', unsafe_allow_html=True)

# st.markdown("---") # Visual separator

# # Inner App Title (as seen under the navigation bar)
# st.markdown("## NISR 2025 Big Data Hackathon")
# st.markdown("### Ending Hidden Hunger: Rwanda Data Challenge")


# # -----------------------------
# # 1. Load preprocessed data (Existing logic)
# # -----------------------------
# try:
#     df = pd.read_csv("outputs/policy_briefs_by_risk_socio.csv")
#     gdf = gpd.read_file("data/rwanda_districts.geojson")
# except FileNotFoundError:
#     st.error("Error: Data files not found. Please ensure 'outputs/policy_briefs_by_risk_socio.csv' and 'data/rwanda_districts.geojson' exist.")
#     st.stop()
# except Exception as e:
#     st.error(f"An error occurred during data loading: {e}")
#     st.stop()

# # -----------------------------
# # 2. Safe parser for list-like strings (Existing logic)
# # -----------------------------
# def safe_parse_list(val):
#     if isinstance(val, list): return val
#     if pd.isna(val): return []
#     try:
#         cleaned = str(val).strip()
#         # The complex parsing logic is kept for safety based on your original code
#         if not cleaned.startswith("["): cleaned = "[" + cleaned + "]"
#         cleaned = cleaned.replace(", ", '","').replace("[", '["').replace("]", '"]')
#         return ast.literal_eval(cleaned)
#     except Exception:
#         return [str(val)]

# # Apply parsing
# df["Root_Causes"] = df["Root_Causes"].astype(str)
# df["Health_Rec"] = df["Health_Rec"].apply(safe_parse_list)
# df["Agri_Rec"] = df["Agri_Rec"].apply(safe_parse_list)
# df["Edu_Rec"] = df["Edu_Rec"].apply(safe_parse_list)

# # -----------------------------
# # 3. Sidebar filters (Keeping for functionality, but moving the main UI elements)
# # -----------------------------
# with st.sidebar:
#     st.title("Filters")
#     risk_levels = st.multiselect(
#         "Select Risk Levels",
#         options=df["Risk_Level"].unique(),
#         default=df["Risk_Level"].unique()
#     )
#     province_filter = st.text_input("Filter by Province (optional)")

# df_filtered = df[df["Risk_Level"].isin(risk_levels)]

# # -----------------------------
# # 4. Merge GeoDataFrames (Existing logic)
# # -----------------------------
# for col in gdf.columns:
#     if "date" in col.lower():
#         gdf = gdf.drop(columns=[col])

# gdf["district"] = gdf["district"].str.strip().str.title()
# df_filtered["District"] = df_filtered["District"].str.strip().str.title()
# gdf = gdf.merge(df_filtered, left_on="district", right_on="District", how="left")

# # -----------------------------
# # 5. Interactive map setup (Simplified legend placement)
# # -----------------------------
# m = folium.Map(location=[-1.95, 30.06], zoom_start=8, tiles="cartodbpositron")
# color_map = {"High": "red", "Medium": "orange", "Low": "green"}

# if "selected_district" not in st.session_state:
#     st.session_state.selected_district = None

# def style_function(feature):
#     risk = feature["properties"].get("Risk_Level", "Low") # Use .get with a default for safe merging
#     return {
#         "fillOpacity": 0.7,
#         "weight": 0.5,
#         "fillColor": color_map.get(risk, "gray"),
#         "color": "black"
#     }

# # Add GeoJson
# folium.GeoJson(
#     gdf,
#     name="Rwanda Districts",
#     style_function=style_function,
#     highlight_function=lambda x: {"weight": 3, "color": "blue"},
#     tooltip=folium.GeoJsonTooltip(fields=["district", "Risk_Level"], aliases=["District:", "Risk Level:"]),
# ).add_to(m)

# # The image doesn't show an explicit legend, so we remove the complex HTML legend
# # and rely on the color scheme and sidebar filter.

# # -----------------------------
# # 6. Dummy Data for Cloned Charts (Needed to match the image)
# # -----------------------------
# def get_dummy_data():
#     # Stunting Risk Districts Data (for the bar chart)
#     risk_districts = df_filtered["Risk_Level"].value_counts(normalize=True).mul(100).round(1).reset_index()
#     risk_districts.columns = ['Risk_Level', 'Percentage']
    
#     # Top 5 High-Risk Trend Data (for the line chart)
#     years = [2020, 2021, 2022, 2023, 2024]
#     trend_data = pd.DataFrame({
#         'Year': years,
#         'Risk_Pct': [5, 6, 7.5, 8.5, 9], # Simulated trend
#         'Lower_Risk_Index': [4, 5, 5.5, 6, 6.5] # Simulated second line
#     })
#     return risk_districts, trend_data

# risk_districts_df, trend_df = get_dummy_data()

# # Calculate overall percentage for the metric card
# total_high_risk = len(df_filtered[df_filtered["Risk_Level"] == "High"])
# total_districts = len(df_filtered)
# stunting_risk_pct = (total_high_risk / total_districts) * 100 if total_districts > 0 else 0

# # -----------------------------
# # 7. Layout: MAIN CONTENT (Cloning the Image's 3-row, 2-column structure)
# # -----------------------------

# # --- ROW 1: Map (Left) and Metrics/Bar Chart (Right) ---
# col_map, col_metric = st.columns([7, 3])

# with col_map:
#     # --- Map Container (Mimics the card) ---
#     with st.container():
#         st_folium(m, width="100%", height=450, returned_objects=[])
#         # Add the 'High Risk' label as an overlay (best done with folium popups or markers for true placement)
#         # For simplicity in Streamlit, we'll use a markdown call that suggests its location
#         st.markdown(
#             f"""
#             <div style="text-align: right; margin-top: -50px; margin-right: 10px; font-weight: bold; color: white; background: rgba(0,0,0,0.5); padding: 5px; border-radius: 5px; width: 150px; float: right;">
#                 High Risk: 45%<br>Deficiency: 30%
#             </div>
#             """, unsafe_allow_html=True
#         )

# with col_metric:
#     # --- Metric Card (Mimics the card) ---
#     with st.container():
#         # Metric: Overall Stunting Risk Districts %
#         st.markdown(f'<h1 style="color: #c42f2f; margin-bottom: 0px;">{stunting_risk_pct:.0f}% <span style="font-size: 0.5em; color: #c42f2f;">↓</span></h1>', unsafe_allow_html=True)
#         st.markdown("Stunting Risk Districts")
        
#         # Bar Chart: Risk Distribution
#         fig_bar = px.bar(
#             risk_districts_df, 
#             x='Risk_Level', 
#             y='Percentage',
#             color='Risk_Level',
#             color_discrete_map={'High': '#3498DB', 'Medium': '#FFC300', 'Low': '#27AE60'},
#             labels={'Risk_Level': '', 'Percentage': ''},
#             height=200
#         )
#         fig_bar.update_layout(
#             margin=dict(l=0, r=0, t=0, b=0),
#             showlegend=False,
#             xaxis={'visible': True, 'showticklabels': True},
#             yaxis={'visible': False, 'showticklabels': False}
#         )
#         st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})
        
#         st.markdown(f"**Key Risk Factors:** Drought, Low Education, Market Access")

# # --- ROW 2: Indicator Selector (Left) and Trend Chart (Right) ---
# col_indicator, col_trend = st.columns(2)

# with col_indicator:
#     # --- Indicator Selector Card (Mimics the card) ---
#     with st.container():
#         st.markdown("### Indicator")
#         # Simulate the custom selector look with checkboxes and radio buttons
#         st.checkbox("Vitamin A Deficiency", value=True)
#         st.checkbox("Combined Risk Index", value=True)
        
#         st.markdown("---")
        
#         col_year, col_dist = st.columns([1, 1])
#         with col_year:
#             st.selectbox("Year", options=['2020-2024'], label_visibility="collapsed")
#         with col_dist:
#             st.radio("District", options=['All Districts', 'Select District'], index=0, horizontal=True)


# with col_trend:
#     # --- Trend Chart Card (Mimics the card) ---
#     with st.container():
#         st.markdown("### Top 5 High-Risk Trend (2020-2024)")
        
#         # Line Chart: Trend
#         fig_line = px.line(
#             trend_df, 
#             x='Year', 
#             y=['Risk_Pct', 'Lower_Risk_Index'],
#             labels={'value': '% Risk', 'variable': 'Indicator'},
#             color_discrete_map={'Risk_Pct': '#27AE60', 'Lower_Risk_Index': '#FFC300'},
#             height=280
#         )
#         fig_line.update_layout(
#             margin=dict(l=20, r=20, t=30, b=20),
#             legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
#         )
#         st.plotly_chart(fig_line, use_container_width=True, config={'displayModeBar': False})


# # --- ROW 3: Call to Action Button ---
# st.markdown("---")
# col_btn, _ = st.columns([1, 4])
# with col_btn:
#     st.button("Explore Data-Driven Solutions", type="primary")

# # -----------------------------
# # 8. District Recommendations (Moved to the bottom for less visual clutter)
# # -----------------------------
# st.markdown("## District Specific Recommendations (Click on Map)")
# st.warning("Note: The original interactive map logic is kept. Click a district on the map above for recommendations to appear below.")

# if st.session_state.selected_district:
#     district_data = df_filtered[df_filtered["District"] == st.session_state.selected_district]
#     if not district_data.empty:
#         row = district_data.iloc[0]
#         st.markdown(f"### Interventions for {row['District']} (Risk: {row['Risk_Level']})")
#         st.markdown(f"**Root Causes:** {row['Root_Causes']}")
        
#         col_h, col_a, col_e = st.columns(3)
#         with col_h:
#             with st.expander("Health Recommendations 🏥"):
#                 for rec in safe_parse_list(row["Health_Rec"]):
#                     st.markdown(f"- {rec}")
#         with col_a:
#             with st.expander("Agriculture Recommendations 🌾"):
#                 for rec in safe_parse_list(row["Agri_Rec"]):
#                     st.markdown(f"- {rec}")
#         with col_e:
#             with st.expander("Education Recommendations 🎓"):
#                 for rec in safe_parse_list(row["Edu_Rec"]):
#                     st.markdown(f"- {rec}")
#     else:
#         st.info(f"No detailed data available for {st.session_state.selected_district} under current filters.")
# else:
#     st.info("Click on a district on the map above to display specific recommendations here.")

# # -----------------------------
# # End
# # -----------------------------
# st.success("✅ UI Refactoring complete! Please run this code with your data files.")














# dashboard.py

import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import ast

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(page_title="Rwanda Malnutrition Risk Dashboard", layout="wide")

# -----------------------------
# Custom CSS for clean UI
# -----------------------------
st.markdown("""
<style>
    /* Top navbar */
    .top-nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: #0a1931;
        padding: 12px 25px;
        border-radius: 8px;
        color: white;
    }
    .nav-links span {
        margin: 0 15px;
        cursor: pointer;
        font-weight: 500;
    }
    .card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .cta-btn {
        background-color: #2563eb;
        color: white;
        padding: 15px 25px;
        font-size: 18px;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Top Navigation
# -----------------------------
st.markdown("""
<div class="top-nav">
    <div><b>NISR 2025 Big Data Hackathon</b></div>
    <div class="nav-links">
        <span>Home</span>
        <span>Challenges</span>
        <span>Solutions</span>
    </div>
    <div>🇷🇼 Team Uhuru</div>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# Load data
# -----------------------------
df = pd.read_csv("outputs/policy_briefs_by_risk_socio.csv")

def safe_parse_list(val):
    if isinstance(val, list):
        return val
    if pd.isna(val):
        return []
    try:
        return ast.literal_eval(val)
    except:
        return [str(val)]

df["Health_Rec"] = df["Health_Rec"].apply(safe_parse_list)
df["Agri_Rec"] = df["Agri_Rec"].apply(safe_parse_list)
df["Edu_Rec"] = df["Edu_Rec"].apply(safe_parse_list)

# -----------------------------
# Hero Title
# -----------------------------
st.markdown("## Ending Hidden Hunger: Rwanda Data Challenge")

# -----------------------------
# Layout: Map + Summary Card
# -----------------------------
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🗺️ Rwanda District Risk Map")

    gdf = gpd.read_file("data/rwanda_districts.geojson")
    gdf["district"] = gdf["district"].str.strip().str.title()
    df["District"] = df["District"].str.strip().str.title()
    gdf = gdf.merge(df, left_on="district", right_on="District", how="left")

    m = folium.Map(location=[-1.95, 30.06], zoom_start=8, tiles="cartodbpositron")
    color_map = {"High": "red", "Medium": "orange", "Low": "green"}

   # Convert non-geometry fields to string (fix Timestamp issue)
for col in gdf.columns:
    if col != "geometry":
        gdf[col] = gdf[col].astype(str)

folium.GeoJson(
    gdf,
    style_function=lambda feature: {
        "fillColor": color_map.get(feature["properties"].get("Risk_Level"), "gray"),
        "color": "black",
        "weight": 0.5,
        "fillOpacity": 0.6,
    },
    tooltip=folium.GeoJsonTooltip(fields=["district", "Risk_Level"]),
).add_to(m)

st_folium(m, width=750, height=500)
st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📊 Summary")
    st.metric("Stunting Risk Districts", "15%", "-5%")
    st.metric("High Risk", "45%")
    st.metric("Deficiency", "30%")

    # Example Bar Chart
    risk_factors = pd.DataFrame({
        "Factor": ["Drought", "Low Education", "Market Access"],
        "Value": [20, 15, 18]
    })
    fig = px.bar(risk_factors, x="Factor", y="Value", title="Key Risk Factors")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Layout: Indicator + High Risk Trends
# -----------------------------
col3, col4 = st.columns([1, 1])

with col3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    indicator = st.selectbox("Indicator", ["Vitamin A Deficiency", "Combined Risk Index"])
    year = st.slider("Year", 2020, 2024, 2022)
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📈 Top 5 High-Risk Districts")
    high_risk = pd.DataFrame({
        "Year": [2020, 2021, 2022, 2023, 2024],
        "Rate": [5, 6.5, 7, 8, 9]
    })
    fig2 = px.line(high_risk, x="Year", y="Rate", markers=True)
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Recommendations Section
# -----------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("📌 Recommendations")

district = st.selectbox("Select District", sorted(df["District"].unique()))
row = df[df["District"] == district].iloc[0]

st.write(f"**Root Causes:** {row['Root_Causes']}")

tab1, tab2, tab3 = st.tabs(["🏥 Health", "🌾 Agriculture", "🎓 Education"])
with tab1:
    for rec in row["Health_Rec"]:
        st.markdown(f"- {rec}")
with tab2:
    for rec in row["Agri_Rec"]:
        st.markdown(f"- {rec}")
with tab3:
    for rec in row["Edu_Rec"]:
        st.markdown(f"- {rec}")
st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# CTA
# -----------------------------
st.markdown('<div class="cta-btn">Explore Data-Driven Solutions</div>', unsafe_allow_html=True)










