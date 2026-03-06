import requests
import math


def haversine_distance(coord1, coord2):
    """
    fallback distance if OSRM fails
    """
    lat1, lon1 = coord1
    lat2, lon2 = coord2

    R = 6371000  # meters

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)

    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2

    return int(2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a)))


def create_distance_matrix(locations):

    try:

        # build OSRM coordinate string
        coords = ";".join([f"{lng},{lat}" for lat, lng in locations])

        url = f"http://router.project-osrm.org/table/v1/driving/{coords}?annotations=distance"

        response = requests.get(url, timeout=5)

        if response.status_code != 200:
            raise Exception("OSRM failed")

        data = response.json()

        if "distances" not in data:
            raise Exception("Invalid OSRM response")

        distances = data["distances"]

        matrix = []

        for row in distances:
            matrix.append([int(d) if d is not None else 0 for d in row])

        return matrix

    except Exception as e:

        # fallback to haversine distance if OSRM fails
        n = len(locations)
        matrix = [[0 for _ in range(n)] for _ in range(n)]

        for i in range(n):
            for j in range(n):
                if i != j:
                    matrix[i][j] = haversine_distance(locations[i], locations[j])

        return matrix