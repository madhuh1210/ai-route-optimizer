import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
import time

API_URL = "http://127.0.0.1:8000/optimize-route"

st.set_page_config(layout="wide")

st.title("🚚 Delivery Route Optimization Dashboard")

# -----------------------------
# Fetch optimized routes
# -----------------------------
try:

    response = requests.get(API_URL, timeout=30)

    if response.status_code != 200:
        st.error(f"Backend API error: {response.status_code}")
        st.write(response.text)
        st.stop()

    data = response.json()

    if not isinstance(data, dict):
        st.error("Invalid response from backend")
        st.stop()

except requests.exceptions.ConnectionError:
    st.error("Backend server not reachable at http://127.0.0.1:8000")
    st.stop()

except requests.exceptions.ReadTimeout:
    st.warning("Backend computing routes... retrying")
    time.sleep(3)
    st.rerun()

except Exception as e:
    st.error(f"API error: {e}")
    st.stop()


# -----------------------------
# Create base map
# -----------------------------
m = folium.Map(
    location=[13.02, 80.23],
    zoom_start=11,
    control_scale=True
)

truck_colors = [
    "red",
    "blue",
    "green",
    "purple",
    "orange"
]

# -----------------------------
# Process clusters
# -----------------------------
for cluster_name, cluster in data.items():

    if not isinstance(cluster, dict):
        continue

    hub = cluster.get("hub")
    locations = cluster.get("locations", [])
    routes = cluster.get("vehicle_routes", [])

    if not hub:
        continue

    # Draw hub
    folium.Marker(
        location=hub,
        popup="Farmer Hub",
        icon=folium.Icon(color="black", icon="home"),
    ).add_to(m)

    # -----------------------------
    # Draw each truck route
    # -----------------------------
    for truck_id, route in enumerate(routes):

        if not route:
            continue

        color = truck_colors[truck_id % len(truck_colors)]
        prev_point = hub

        stop_number = 0

        for node in route:

            # skip hub nodes
            if node == 0:
                continue

            stop_number += 1

            try:
                lat, lng = locations[node - 1]
            except:
                continue

            truck_number = truck_id + 1

            label = f"{truck_number}-{stop_number}"

            # -----------------------------
            # Delivery marker
            # -----------------------------
            folium.CircleMarker(
                location=[lat, lng],
                radius=10,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.9,
                popup=f"Truck {truck_number} | Stop {stop_number}",
            ).add_to(m)

            folium.Marker(
                location=[lat, lng],
                icon=folium.DivIcon(
                    html=f"""
                    <div style="
                        color:white;
                        font-weight:bold;
                        text-align:center;
                        margin-top:-28px;">
                        {label}
                    </div>
                    """
                ),
            ).add_to(m)

            # -----------------------------
            # Draw road route
            # -----------------------------
            try:

                url = f"http://router.project-osrm.org/route/v1/driving/{prev_point[1]},{prev_point[0]};{lng},{lat}?overview=full&geometries=geojson"

                r = requests.get(url, timeout=10)

                if r.status_code == 200:

                    route_data = r.json()

                    coords = route_data["routes"][0]["geometry"]["coordinates"]

                    road_points = [(c[1], c[0]) for c in coords]

                    folium.PolyLine(
                        road_points,
                        color=color,
                        weight=4,
                        opacity=0.9,
                    ).add_to(m)

                else:

                    folium.PolyLine(
                        [prev_point, (lat, lng)],
                        color=color,
                        weight=2,
                        dash_array="5",
                    ).add_to(m)

            except:

                folium.PolyLine(
                    [prev_point, (lat, lng)],
                    color=color,
                    weight=2,
                    dash_array="5",
                ).add_to(m)

            prev_point = (lat, lng)


# -----------------------------
# Render map
# -----------------------------
st_folium(m, width=1200, height=700)

# -----------------------------
# Auto refresh dashboard
# -----------------------------
time.sleep(10)
st.rerun()