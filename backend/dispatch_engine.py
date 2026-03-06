from database import conn
from clustering import run_clustering
import time
from datetime import datetime, timedelta


def dispatch_engine():

    while True:

        print("\n==============================")
        print("[DISPATCH ENGINE] Dispatching batch")
        print("==============================")

        batch_end = datetime.now()
        batch_start = batch_end - timedelta(minutes=15)

        with conn.cursor() as cursor:

            # Fetch only orders in this batch window
            cursor.execute(
                """
                SELECT id
                FROM orders
                WHERE dispatched = FALSE
                AND created_at >= %s
                AND created_at < %s
                """,
                (batch_start, batch_end)
            )

            orders = cursor.fetchall()

            print("Orders ready:", len(orders))

            if len(orders) > 0:

                # Run clustering for this batch
                run_clustering()

                # Dispatch only this batch
                cursor.execute(
                    """
                    UPDATE orders
                    SET dispatched = TRUE
                    WHERE dispatched = FALSE
                    AND created_at >= %s
                    AND created_at < %s
                    """,
                    (batch_start, batch_end)
                )

                conn.commit()

                print("[DISPATCH] Orders dispatched successfully")

        # wait 15 minutes for next batch
        time.sleep(900)