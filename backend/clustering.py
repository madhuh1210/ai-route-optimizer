import numpy as np
from sklearn.cluster import DBSCAN
from database import cursor, conn

def run_clustering():

    # fetch orders from database
    cursor.execute("SELECT id, latitude, longitude FROM orders")

    orders = cursor.fetchall()

    if len(orders) == 0:
        return "No orders found"

    # convert coordinates into numpy array
    coords = np.array([[o[1], o[2]] for o in orders])

    # DBSCAN clustering
    db = DBSCAN(eps=0.02, min_samples=2).fit(coords)

    labels = db.labels_

    # update cluster id in database
    for i, order in enumerate(orders):

        cluster_id = int(labels[i])

        cursor.execute(
            "UPDATE orders SET cluster_id=%s WHERE id=%s",
            (cluster_id, order[0])
        )

    conn.commit()

    return labels