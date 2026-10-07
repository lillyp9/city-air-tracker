import os 
import psycopg2
from dotenv import load_dotenv

#load env file
load_dotenv()

conn = psycopg2.connect(
    host = os.getenv("DB_Host"),
    port = os.getenv("DB_Port"),
    dbname = os.getenv("DB_Name"),
    user = os.getenv("DB_USER"),
    password = os.getenv("DB_PASSWORD")
)

cur = conn.cursor()

#create the primary table (Main/Parent table)
cur.execute("""
CREATE TABLE IF NOT EXISTS city_table(
    city_id   SERIAL PRIMARY KEY,
    city_name VARCHAR(100) NOT NULL, 
    state CHAR(2) NOT NULL,
    lat NUMERIC(9,6) NOT NULL,
    lon NUMERIC(9,6) NOT NULL,
    UNIQUE (city_name, state)
)
""")
conn.commit()

#create child/second table 
cur.execute("""
CREATE TABLE IF NOT EXISTS air_pollution_table (
    id BIGSERIAL PRIMARY KEY,
    aqi INT,
    city_id INT NOT NULL REFERENCES city_table(city_id),
    reading_time_utc TIMESTAMP NOT NULL,
    carbon_monoxide NUMERIC,
    nitric_oxide NUMERIC,
    nitrogen_dioxide NUMERIC,
    ozone NUMERIC,
    sulfur_dioxide NUMERIC,
    fine_particles NUMERIC,
    coarse_particles NUMERIC,
    ammonia NUMERIC,
    UNIQUE (city_id, reading_time_utc)

);
""")
conn.commit()

print("Successfully created")

#closed script 
cur.close()
conn.close()

#Numeric (9,6) mean 3 digits before decimal . 