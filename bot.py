import os
import psycopg2
from datetime import date, timedelta
from dotenv import load_dotenv
from google import genai

#load from env file 
load_dotenv()
#api key for gemini api
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = "gemini-3.6-flash"

#connect to the RDS
def get_connection():
    return psycopg2.connect(
        host     = os.getenv("DB_Host"),
        port     = os.getenv("DB_Port"),
        dbname   = os.getenv("DB_Name"),
        user     = os.getenv("DB_USER"),
        password = os.getenv("DB_PASSWORD")
    )

#pull the reading data for one city of the date range 
def get_city_readings(cur, city_name, state, start_date, end_date):

    #create query 
    cur.execute(""" 
        
        SELECT air_pollution_table.reading_time_utc, air_pollution_table.aqi,
               air_pollution_table.carbon_monoxide, air_pollution_table.nitric_oxide, 
               air_pollution_table.nitrogen_dioxide, air_pollution_table.ozone, 
               air_pollution_table.sulfur_dioxide, air_pollution_table.fine_particles, 
               air_pollution_table.coarse_particles, air_pollution_table.ammonia
        FROM air_pollution_table
        JOIN city_table ON air_pollution_table.city_id = city_table.city_id
        WHERE city_table.city_name = %s AND city_table.state = %s
          AND air_pollution_table.reading_time_utc >= %s AND air_pollution_table.reading_time_utc <= %s
        ORDER BY air_pollution_table.reading_time_utc;
    """, (city_name, state, start_date, end_date))
    return cur.fetchall()

#give ai the data and aask to return summary/reply:
def get_ai(instruction, data):

    response = client.models.generate_content(
        model=MODEL,
        contents=f"{instruction}\n\nData:\n{data}"
    )
    return response.text

#summary in english of th reading of the city for the date range
def summarize(rows, city_name, state, start_date, end_date):
    data = "\n".join(str(row) for row in rows)
    #system prompt togive context to the ai model 
    instruction = (
        f"You are provided with the data and describing the air quality data for {city_name}, {state} from {start_date} to {end_date}."
        "Each row is (timestamp, AQI range from 1- 5 where 1 is very good ,2 is good, 3 is moderate, 4 is poor, 5 is very poor),"
        "Air pollution data (carbon monoxide, nitric oxide, nitrogen dioxide, ozone, sulfur dioxide, fine particles, coarse particles, ammonia) in micrograms per cubic meter."
        "Do not list every reading, instead make sure to provide a summary ."
        )
    return get_ai(instruction, data)

#Health advice based on the air data for the city.
def health_data_advice(rows, city_name, state):
    #gives precaution output , NOT medical advice , just general health advice based on the data provided.
    data = "\n".join(str(row) for row in rows)
    instruction = (
        f"Air quality data readings for {city_name}, {state}."
        "AQI is range from 1 - 5 where 1 is very good and 5 is very poor. Pollutants are in micrograms per cibic meter."
        "Provide a summary suggesting health precautions, especially for sensitive groups like childrens, older adults, and people with asthma."
        "Have a friendly and informative tone as well as a disclaimer that this is not medical advice, just general health advice for users discretion."

    )
    return get_ai(instruction, data)

#
if __name__ == "__main__":
    conn = get_connection()
    cur = conn.cursor()

    # show what's available so they know what to type
    cur.execute("SELECT city_name, state FROM city_table ORDER BY state")
    cities = cur.fetchall()
    print("Available cities:")
    print(", ".join(f"{c}, {s}" for c, s in cities))
    print()
    #city, state, 
    city_name = input("City:").strip()
    state = input("State:").strip().upper()
    #comment out the days to look back at since it could hit the token limit annd now we are asking the start and end date to be more specific.
    #days = int(input("How many days back to look for data?"))
    #end_date = date.today()
    #start_date = end_date - timedelta(days=days)

    #dates
    try:
        start_date = date.fromisoformat(input("Start date (YYYY-MM-DD): ").strip())
        end_date   = date.fromisoformat(input("End date (YYYY-MM-DD): ").strip())
    except ValueError:
        print("Dates must be in YYYY-MM-DD format, e.g. 2026-08-27")
        cur.close()
        conn.close()
        exit()

    if start_date > end_date:
        print("Start date must be before end date.")
        cur.close()
        conn.close()
        exit()
        #guard for the data range being too long, hit the token limit of the model
    if (end_date - start_date).days > 14:
        print("Please choose a range of 14 days or less.")
        cur.close()
        conn.close()
        exit()


    rows = get_city_readings(cur, city_name, state, start_date, end_date)

    if not rows:
        print(f"No data found for {city_name}, {state}")
    else:
        print(f"Found {len(rows)} readings for {city_name}, {state}\n")

        print("Summary of air quality data:")
        summary = summarize(rows, city_name, state, start_date, end_date)
        print(summary)

        print("Health advice")
        print(health_data_advice(rows, city_name, state))

    cur.close()
    conn.close()









    #test it out with a city , HARDCODE
    #city_name = "Baltimore"
    #state = "MD"
    #end_date = date.today()
    #start_date = end_date -timedelta(days=3)

    #rows = get_city_readings(cur, city_name, state, start_date, end_date)
    #print(f"Found {len(rows)} readings for {city_name}, {state}\n")

    #print("Summary of air quality data:")
    #summary = summarize(rows, city_name, state, start_date, end_date)
    #print(summary)

    #print("Health advice")
    #print(health_data_advice(rows, city_name, state))

  
