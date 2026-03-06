import time
from clustering import run_clustering

ROUTE_UPDATE_INTERVAL = 10  # seconds


def start_auto_routing():

    while True:

        try:
            run_clustering()
            print("Auto clustering updated")

        except Exception as e:
            print("Auto routing error:", e)

        time.sleep(ROUTE_UPDATE_INTERVAL)