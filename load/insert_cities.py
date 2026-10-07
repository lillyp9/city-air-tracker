import os
import json
import psycopg2
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host     = os.getenv("DB_Host"),
    port     = os.getenv("DB_Port"),
    dbname   = os.getenv("DB_Name"),
    user     = os.getenv("DB_USER"),
    password = os.getenv("DB_PASSWORD")
)
cur = conn.cursor()

#open the city_table.py
with open ('city_table.json') as file:
    city_table = json.load(file)

#let the database assign ids 
for city in city_table:
    cur.execute("""
     INSERT INTO city_table(city_name, state, lat, lon)
        VALUES (%s, %s, %s, %s) 
        ON CONFLICT (city_name ,state) DO NOTHING
        """, (city['city_name'], city['state'], city['lat'], city['lon']))

conn.commit()

#read back what the database actaully gave out 
cur.execute("SELECT city_id, city_name, state FROM city_table ORDER BY city_id")
rows = cur.fetchall()

for row in rows:
    print(row)

print(f"\n{len(rows)} cities in city_table")

cur.close()
conn.close()
