import os
import psycopg2
from datetime import date, timedelta
from dotenv import load_dotenv
from daily_info import load_day

load_dotenv()

START_DATE = date(2026, 1, 1)   #teammate changes this to the date of their choosing 
END_DATE   = date.today() - timedelta(days=1)

#bottom dates commented out to debug to see if there is any missing data. End conclusion: its an API bug not in our end with the code.

#START_DATE = date(2026, 8, 30)
#END_DATE   = date(2026, 8, 31)
#debugged again - 12 rows that are null for Baltimore , its the same issue that is realted to the APi bug 
#conn = psycopg2.connect(
#    host=os.getenv("DB_Host"), 
 #   port=os.getenv("DB_Port"),
 #   dbname=os.getenv("DB_Name"), 
  #  user=os.getenv("DB_USER"),
   # password=os.getenv("DB_PASSWORD")
#)
def get_connection():
    return psycopg2.connect(
        host     = os.getenv("DB_Host"),
        port     = os.getenv("DB_Port"),
        dbname   = os.getenv("DB_Name"),
        user     = os.getenv("DB_USER"),
        password = os.getenv("DB_PASSWORD")
    )
#cur = conn.cursor()
#query to get the city info from the city table , all 

total = 0
current = START_DATE

while current <= END_DATE:
    try:
        #fresh connection each day so a drop connection doesnt end the entire run.
        conn = get_connection()
        cur = conn.cursor()

        #query to get the city information from the city table
        cur.execute("SELECT city_id, city_name, state, lat, lon FROM city_table")
        #fetch all 
        city_table = cur.fetchall()
 
        total += load_day(current, cur, city_table)
        conn.commit() # commit each day ,a crash keeps what's done
        cur.close()
        conn.close()

    except psycopg2.OperationalError as e:
        print(f"Connection lost on {current} , rerun the script ")
        print(e)
                           
    current += timedelta(days=1)

print(f"\nBackfill complete: {total} rows")

cur.close()
conn.close()
