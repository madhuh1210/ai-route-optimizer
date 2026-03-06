import numpy as np
from sklearn.cluster import DBSCAN
from database import conn


def run_clustering():

    # create thread-safe cursor
    with conn.cursor() as cursor:

        # fetch only orders not dispatched yet
        cursor.execute("""
            SELECT id, latitude, longitude
            FROM orders
            WHERE dispatched = FALSE
        """)

        orders = cursor.fetchall()

        if len(orders) == 0:
            return []

        coords = np.array([[o[1], o[2]] for o in orders])

        # DBSCAN clustering
        db = DBSCAN(eps=0.05, min_samples=2).fit(coords)

        labels = db.labels_

        # convert noise (-1) into unique clusters
        max_cluster = labels.max() + 1

        for i in range(len(labels)):
            if labels[i] == -1:
                labels[i] = max_cluster
                max_cluster += 1

        # update cluster id in DB
        for i, order in enumerate(orders):

            cursor.execute(
                """
                UPDATE orders
                SET cluster_id = %s
                WHERE id = %s
                """,
                (int(labels[i]), order[0])
            )

        conn.commit()

    print("Auto clustering updated")

    return labels