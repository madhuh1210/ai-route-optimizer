import streamlit as st
import folium
import requests
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster

st.set_page_config(layout="wide")

st.title("🚚 Delivery Route Optimization Dashboard")

# Call backend API
response = requests.get("http://127.0.0.1:8000/optimize-route")
data = response.json()

# Create map centered around Chennai
m = folium.Map(location=[13.00, 80.25], zoom_start=12)

colors = ["red", "blue", "green", "purple", "orange"]

cluster_index = 0

for cluster_name, cluster_data in data.items():

    if cluster_data == "Not enough orders":
        continue

    locations = cluster_data["locations"]
    route = cluster_data["optimized_route"]

    color = colors[cluster_index % len(colors)]
    cluster_index += 1

    # Create marker cluster for overlapping markers
    marker_cluster = MarkerCluster().add_to(m)

    # Add markers
    for i, loc in enumerate(locations):
        folium.Marker(
            location=loc,
            popup=f"{cluster_name} - Order {i+1}",
            icon=folium.Icon(color=color, icon="info-sign")
        ).add_to(marker_cluster)

    # Draw optimized route
    route_coords = [locations[i] for i in route]

    folium.PolyLine(
        route_coords,
        color=color,
        weight=4,
        opacity=0.8,
        tooltip=f"{cluster_name} route"
    ).add_to(m)

# Display map
st_folium(m, width=1200, height=600)