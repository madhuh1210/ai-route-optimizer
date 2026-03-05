import requests

def get_road_distance(coord1, coord2):

    lat1, lon1 = coord1
    lat2, lon2 = coord2

    url = f"http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=false"

    try:
        response = requests.get(url)
        data = response.json()

        if data["code"] != "Ok":
            return 9999

        distance = int(data["routes"][0]["distance"] / 100)

        return distance

    except:
        return 9999


def create_distance_matrix(locations):

    matrix = []

    for i in range(len(locations)):
        row = []

        for j in range(len(locations)):

            if i == j:
                row.append(0)

            else:
                distance = get_road_distance(locations[i], locations[j])
                row.append(distance)

        matrix.append(row)

    return matrix