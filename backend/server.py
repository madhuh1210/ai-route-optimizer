from fastapi import FastAPI
from database import conn, cursor
from clustering import run_clustering
from routing import optimize_route
from distance import create_distance_matrix

app = FastAPI()


@app.get("/")
def home():
    return {"message": "Route optimization backend running"}


@app.post("/create-order")
def create_order(user_id: str, address: str, lat: float, lng: float):

    cursor.execute(
        "INSERT INTO orders (user_id,address,latitude,longitude) VALUES (%s,%s,%s,%s)",
        (user_id, address, lat, lng)
    )

    conn.commit()

    return {"message": "Order placed"}


@app.get("/cluster-orders")
def cluster_orders():

    labels = run_clustering()

    return {"clusters": labels.tolist()}


@app.get("/optimize-route")
def optimize_delivery_route():

    # get all clusters except noise (-1)
    cursor.execute(
        "SELECT DISTINCT cluster_id FROM orders WHERE cluster_id != -1"
    )

    clusters = cursor.fetchall()

    routes = {}

    for cluster in clusters:

        cluster_id = cluster[0]

        cursor.execute(
            "SELECT latitude, longitude FROM orders WHERE cluster_id = %s",
            (cluster_id,)
        )

        locations = cursor.fetchall()

        if len(locations) < 2:
            routes[f"cluster_{cluster_id}"] = "Not enough orders"
            continue

        # create distance matrix
        distance_matrix = create_distance_matrix(locations)

        # optimize route
        route = optimize_route(distance_matrix)

        routes[f"cluster_{cluster_id}"] = {
            "locations": locations,
            "optimized_route": route
        }

    return routes