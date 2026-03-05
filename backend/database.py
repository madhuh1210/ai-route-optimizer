import psycopg2

conn = psycopg2.connect(
    database="route_optimizer",
    user="postgres",
    password="postgres",
    host="localhost",
    port="5432"
)

cursor = conn.cursor()