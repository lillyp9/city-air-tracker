import os 
import json
import requests
import psycopg2
from datetime import datetime, date, time, timedelta, timezone 
from dotenv import load_dotenv
from zoneinfo import ZoneInfo

#======= Load the api key from the .env file ======
load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")


#====== connect to the RDS
conn = psycopg2.connect(
    host     = os.getenv("DB_Host"),
    port     = os.getenv("DB_Port"),
    dbname   = os.getenv("DB_Name"),
    user     = os.getenv("DB_USER"),
    password = os.getenv("DB_PASSWORD")
)
cur = conn.cursor()

cities = [
    ("Birmingham", "AL"),
    ("Anchorage", "AK"),
    ("Phoenix", "AZ"),
    ("Little Rock", "AR"),
    ("Los Angeles", "CA"),
    ("Denver", "CO"),
    ("Bridgeport", "CT"),
    ("Wilmington", "DE"),
    ("Jacksonville", "FL"),
    ("Atlanta", "GA"),
    ("Honolulu", "HI"),
    ("Boise", "ID"),
    ("Chicago", "IL"),
    ("Indianapolis", "IN"),
    ("Des Moines", "IA"),
    ("Wichita", "KS"),
    ("Louisville", "KY"),
    ("New Orleans", "LA"),
    ("Portland", "ME"),
    ("Baltimore", "MD"),
    ("Boston", "MA"),
    ("Detroit", "MI"),
    ("Minneapolis", "MN"),
    ("Jackson", "MS"),
    ("Kansas City", "MO"),
    ("Billings", "MT"),
    ("Omaha", "NE"),
    ("Las Vegas", "NV"),
    ("Manchester", "NH"),
    ("Newark", "NJ"),
    ("Albuquerque", "NM"),
    ("New York", "NY"),
    ("Charlotte", "NC"),
    ("Fargo", "ND"),
    ("Columbus", "OH"),
    ("Oklahoma City", "OK"),
    ("Portland", "OR"),
    ("Philadelphia", "PA"),
    ("Providence", "RI"),
    ("Charleston", "SC"),
    ("Sioux Falls", "SD"),
    ("Nashville", "TN"),
    ("Houston", "TX"),
    ("Salt Lake City", "UT"),
    ("Burlington", "VT"),
    ("Virginia Beach", "VA"),
    ("Seattle", "WA"),
    ("Charleston", "WV"),
    ("Milwaukee", "WI"),
    ("Cheyenne", "WY"),
]


city_table = []

#==== City Table 
#city id 
#city name 
#state
#lat
#lon

#looping through cities 
for index, (city_name, state) in enumerate(cities, start=1): #put 1 to get the 50 cities 
    #Second API key is geocoding API 
    GEO_URL = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name},{state},US&limit=1&appid={API_KEY}"
   
    #fetch data from API
    response = requests.get(GEO_URL)
    if response.status_code == 200:
        results = response.json()
        #keeps the code continue and print  A MESSAGE
        if not results:
            print(f"Not found: {city_name}, {state}")
            continue
        
        city_entry = {}
        city_entry['city_id'] = index
        city_entry['city_name'] = city_name
        city_entry['state'] = state
        city_entry['lat'] = results[0]['lat']
        city_entry['lon'] = results[0]['lon']
          
        city_table.append(city_entry)
        print(city_entry)
       
with open('city_table.json', 'w') as file:
    json.dump(city_table, file, indent=4)

print(f"Saved {len(city_table)} cities to city_table.json")