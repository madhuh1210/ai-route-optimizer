from fastapi import FastAPI
from database import conn
from clustering import run_clustering
from routing import optimize_route
from distance import create_distance_matrix
from auto_routing import start_auto_routing
from dispatch_engine import dispatch_engine

import threading
import time

app = FastAPI()

# Farmer hub / depot location
FARMER_HUB = (13.0067, 80.2206)  # Adyar


# ------------------------------------------------
# Start background engines
# ------------------------------------------------
@app.on_event("startup")
def start_background_services():

    routing_thread = threading.Thread(target=start_auto_routing)
    routing_thread.daemon = True
    routing_thread.start()

    dispatch_thread = threading.Thread(target=dispatch_engine)
    dispatch_thread.daemon = True
    dispatch_thread.start()

    print("Automatic routing engine started")
    print("Dispatch engine started")


# ------------------------------------------------
# Health check
# ------------------------------------------------
@app.get("/")
def home():

    return {"message": "Route optimization backend running"}


# ------------------------------------------------
# Create order
# ------------------------------------------------
@app.post("/create-order")
def create_order(user_id: str, address: str, lat: float, lng: float):

    with conn.cursor() as cursor:

        cursor.execute(
            """
            INSERT INTO orders (user_id,address,latitude,longitude,dispatched)
            VALUES (%s,%s,%s,%s,FALSE)
            """,
            (user_id, address, lat, lng)
        )

    conn.commit()

    print(f"[ORDER] New order placed → {address}")

    return {"message": "Order placed successfully"}


# ------------------------------------------------
# Run clustering manually
# ------------------------------------------------
@app.get("/cluster-orders")
def cluster_orders():

    labels = run_clustering()

    if isinstance(labels, str):
        return {"message": labels}

    return {"clusters": labels.tolist()}


# ------------------------------------------------
# Optimize delivery routes
# ------------------------------------------------
@app.get("/optimize-route")
def optimize_delivery_route():

    with conn.cursor() as cursor:

        cursor.execute("""
        SELECT DISTINCT cluster_id
        FROM orders
        WHERE cluster_id != -1
        AND dispatched = FALSE
        """)

        clusters = cursor.fetchall()

    cluster_routes = {}

    for cluster in clusters:

        cluster_id = cluster[0]

        with conn.cursor() as cursor:

            cursor.execute("""
            SELECT latitude, longitude
            FROM orders
            WHERE cluster_id = %s
            AND dispatched = FALSE
            """, (cluster_id,))

            orders = cursor.fetchall()

        if len(orders) == 0:
            continue

        locations = [FARMER_HUB] + list(orders)

        distance_matrix = create_distance_matrix(locations)

        num_trucks = min(3, len(orders))

        vehicle_routes = optimize_route(
            distance_matrix,
            num_vehicles=num_trucks
        )

        cleaned_routes = []

        for route in vehicle_routes:

            cleaned = [node for node in route if node != 0]

            cleaned_routes.append(cleaned)

        cluster_routes[f"cluster_{cluster_id}"] = {
            "hub": FARMER_HUB,
            "locations": orders,
            "vehicle_routes": cleaned_routes
        }

    return cluster_routes


# ------------------------------------------------
# Manual dispatch (optional testing endpoint)
# ------------------------------------------------
@app.post("/dispatch-orders")
def dispatch_orders():

    with conn.cursor() as cursor:

        cursor.execute("""
        UPDATE orders
        SET dispatched = TRUE,
        dispatched_at = NOW()
        WHERE dispatched = FALSE
        """)

    conn.commit()

    return {"message": "Orders dispatched manually"}