import os 
import json
import requests
import psycopg2
from datetime import datetime, date, time, timedelta, timezone 
from dotenv import load_dotenv

#======= Load the api key from the .env file ======
load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")


#====== connect to the RDS
def get_connection():
    return psycopg2.connect(
        host     = os.getenv("DB_Host"),
        port     = os.getenv("DB_Port"),
        dbname   = os.getenv("DB_Name"),
        user     = os.getenv("DB_USER"),
        password = os.getenv("DB_PASSWORD")
    )
#=====This section is for the testing:=======
def map_pollution_fields(component):
    """Maps one API air pollution component to schema column names."""
    return {
        'aqi': component['main']['aqi'],
        'carbon_monoxide': component['components']['co'],
        'nitric_oxide': component['components']['no'],
        'nitrogen_dioxide': component['components']['no2'],
        'ozone': component['components']['o3'],
        'sulfur_dioxide': component['components']['so2'],
        'fine_particles': component['components']['pm2_5'],
        'coarse_particles': component['components']['pm10'],
        'ammonia': component['components']['nh3'],
    }

#==== testing session ends here . Continue regular coding =====
def build_time_window(target_date): #this function and parameters would be used for testing 
    # Get the same 24 hour window  
    start = int(datetime.combine(target_date, time(0, 0), tzinfo=timezone.utc).timestamp())
    end   = int(datetime.combine(target_date, time(23, 59), tzinfo=timezone.utc).timestamp())
    return start, end

def load_day(target_date, cur, city_table):
    rows_added = 0
    air_pollution_table = []

    #Columns
        # city_id
        # carbon_monoxide (done)
        #nitric_oxide
        #nitrogen_dioxide
        #ozone
        #sulfur_dioxide
        #fine_particles
        #coarse_particles
        #ammonia
        #datetime (convert)

    #fetch air pollution for every city 
    for city_id, city_name, state, lat, lon in city_table:

        #=========== API URL ================
        #First API key is air pollution API 
        AIR_POLLUTION_HISTORY_URL = f"http://api.openweathermap.org/data/2.5/air_pollution/history?lat={lat}&lon={lon}&appid={API_KEY}&start={start}&end={end}"

        # ======= fetch air pollution data from the API 
        response = requests.get(AIR_POLLUTION_HISTORY_URL, timeout=10)

        if response.status_code != 200:
            print(f"FAILED {city_name}, {state}")
            print(response.json())
            continue

        data = response.json()
        air_components_list = data['list']

        for component in air_components_list:
            #aqi = component['main']['aqi']  # 1-5, 1 is good, 5 is very poor
            # {'co': 137.02, 'no': 0, 'no2': 0.55, 'o3': 18.06, 'so2': 0.01, 'pm2_5': 0.5, 'pm10': 0.54, 'nh3': 0.02}

            # Entry
            air_pollution_entry={}
            air_pollution_entry = map_pollution_fields(component)
            air_pollution_entry['city_id'] = city_id
            air_pollution_entry['aqi'] = component['main']['aqi']
            air_pollution_entry['carbon_monoxide'] = component['components']['co']
            air_pollution_entry['nitric_oxide'] = component['components']['no']
            air_pollution_entry['nitrogen_dioxide'] = component['components']['no2']
            air_pollution_entry['ozone'] = component['components']['o3']
            air_pollution_entry['sulfur_dioxide'] = component['components']['so2']
            air_pollution_entry['fine_particles'] = component['components']['pm2_5']
            air_pollution_entry['coarse_particles'] = component['components']['pm10']
            air_pollution_entry['ammonia'] = component['components']['nh3']

            # Grab dt found in the component object and convert the Unix timestamp
            # to an explicit UTC datetime.
            timestamp = component['dt']
            reading_time = datetime.fromtimestamp(timestamp, tz=timezone.utc)
            air_pollution_entry['datetime'] = reading_time.strftime("%Y-%m-%d %-I:%M %p")

            #Insert these query/reading into RDS
            cur.execute("""
                INSERT INTO air_pollution_table (
                    city_id, reading_time_utc, aqi, carbon_monoxide, nitric_oxide,
                    nitrogen_dioxide, ozone, sulfur_dioxide, fine_particles,
                    coarse_particles, ammonia
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (city_id, reading_time_utc) DO NOTHING
               
            """, (
                city_id,
                              reading_time,
                              air_pollution_entry['aqi'],
                              air_pollution_entry['carbon_monoxide'],
                              air_pollution_entry['nitric_oxide'],
                              air_pollution_entry['nitrogen_dioxide'],
                              air_pollution_entry['ozone'],
                              air_pollution_entry['sulfur_dioxide'],
                              air_pollution_entry['fine_particles'],
                              air_pollution_entry['coarse_particles'],
                              air_pollution_entry['ammonia'],
                          ))
            rows_added += cur.rowcount

            air_pollution_table.append(air_pollution_entry)

        print(f"{city_name}, {state}: {len(air_components_list)} read and loaded")

    print(f"{target_date}: {rows_added} rows added")
    return rows_added


# ===== only runs when you type python3 daily_info.py =====
if __name__ == "__main__":
    conn = get_connection()
    cur = conn.cursor()

    #======= read from the RDS
    cur.execute("SELECT city_id, city_name, state, lat, lon FROM city_table")
    city_table = cur.fetchall()

    #======== pick the day 
    load_day(date.today() - timedelta(days=1), cur, city_table)

    #=== Save to database ====
    conn.commit()

    #====== close connection 
    cur.close()
    conn.close()