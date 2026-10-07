from dash import Dash, dcc, html, Input, Output,dash_table
import plotly.express as px
import pandas as pd
import os
import psycopg
from dotenv import load_dotenv


#--------------------------
#   Loading the BD
#--------------------------
load_dotenv()
def get_connection():
    return psycopg.connect(
        host=os.getenv("DB_Host"),
        port=os.getenv("DB_Port"),
        dbname=os.getenv("DB_Name"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        sslmode="require"
    )

#--------------------------
#   Extracting all 50 cities 
#--------------------------
conn = get_connection()
with conn.cursor() as cursor:
    cursor.execute("""
        SELECT city_id, city_name, state
        FROM city_table
        ORDER BY city_name;
    """)
    cities = cursor.fetchall()
conn.close()


#--------------------------
#   Dash Layout
#--------------------------
app = Dash(__name__)
app.layout = html.Div([

    html.H1("City Air Tracker"),

    #--------------------------
    # City + Date Menu
    #--------------------------
    html.Div([
        html.Div([
            html.Label("Select a city:"),
            dcc.Dropdown(
                id="city-dropdown",
                options=[
                    {
                        "label": city[1],
                        "value": city[0]
                    }
                    for city in cities
                ],
                placeholder="Choose a city"
            )], style={"width": "45%"}),

        html.Div([
            html.Label("Select a date:"),
            dcc.DatePickerSingle(
                id="date-picker",
                placeholder="Select a date"
            )
        ])
    ], style={
        "display": "flex",
        "gap": "30px",
        "alignItems": "end"
    }),

    #--------------------------
    # Error message
    #--------------------------
    html.Div(
        id="error-message",
        style={
            "color": "red",
            "fontWeight": "bold",
            "textAlign": "center",
            "margin": "15px"}
    ),

    html.Hr(),


    #--------------------------
    # Daily average tables
    #--------------------------
    html.H2("Daily Average Pollutant Levels"),

    html.Div([
    # --------------------------------
    # LEFT table
    # --------------------------------
        html.Div([
            html.H3("AQ components daily average"),
            dash_table.DataTable(
                id="daily-average-table",

                columns=[
                    {"name": "Pollutant", "id": "Pollutant"},
                    {"name": "Daily Average", "id": "Daily Average"}],

                style_cell={
                    "textAlign": "center",
                    "padding": "5px",
                    "fontSize": "13px"},
                style_header={
                    "fontWeight": "bold",
                    "fontSize": "13px"})

        ], style={"width": "35%"}),

    #---------------------------------
    # RIGHT table
    #---------------------------------
        html.Div([
            html.H3("AQ components Reference"),
            dash_table.DataTable(
                columns=[{
                    "name": ["", "Qualitative name"],
                    "id": "quality"},
                {
                    "name": ["Pollutant concentration in μg/m³", "SO₂"],
                    "id": "so2"
                },
                {
                    "name": ["Pollutant concentration in μg/m³", "NO₂"],
                    "id": "no2"
                },
                {
                    "name": ["Pollutant concentration in μg/m³", "PM10"],
                    "id": "pm10"
                },
                {
                    "name": ["Pollutant concentration in μg/m³", "PM2.5"],
                    "id": "pm25"
                },
                {
                    "name": ["Pollutant concentration in μg/m³", "O₃"],
                    "id": "o3"
                },
                {
                    "name": ["Pollutant concentration in μg/m³", "CO"],
                    "id": "co"
                }
            ],

                data=[{
                    "quality": "Good",
                    "so2": "[0, 20)",
                    "no2": "[0, 40)",
                    "pm10": "[0, 20)",
                    "pm25": "[0, 10)",
                    "o3": "[0, 60)",
                    "co": "[0, 4400)"},
                {
                    "quality": "Fair",
                    "so2": "[20, 80)",
                    "no2": "[40, 70)",
                    "pm10": "[20, 50)",
                    "pm25": "[10, 25)",
                    "o3": "[60, 100)",
                    "co": "[4400, 9400)"
                },
                {
                    "quality": "Moderate",
                    "so2": "[80, 250)",
                    "no2": "[70, 150)",
                    "pm10": "[50, 100)",
                    "pm25": "[25, 50)",
                    "o3": "[100, 140)",
                    "co": "[9400, 12400)"
                },
                {
                    "quality": "Poor",
                    "so2": "[250, 350)",
                    "no2": "[150, 200)",
                    "pm10": "[100, 200)",
                    "pm25": "[50, 75)",
                    "o3": "[140, 180)",
                    "co": "[12400, 15400)"
                },
                {
                    "quality": "Very Poor",
                    "so2": "≥350",
                    "no2": "≥200",
                    "pm10": "≥200",
                    "pm25": "≥75",
                    "o3": "≥180",
                    "co": "≥15400"
                }],

            merge_duplicate_headers=True,
            style_cell={
                "textAlign": "center",
                "padding": "6px",
                "fontSize": "11px",
                "whiteSpace": "normal",
                "height": "auto"
            },
            style_header={
                "fontWeight": "bold",
                "fontSize": "11px"
            }
        )

        ], style={"width": "60%"})], 
    style={"display": "flex","gap": "15px","alignItems": "flex-start","width": "100%"}),


    #--------------------------
    # AQI graph
    #--------------------------
    html.H2("Average AQI by Hour"),
    dcc.Graph(id="aqi-hourly-graph",style={"height": "300px"}),

    #--------------------------
    # Best + Worst AQI
    #-------------------------- 
    html.Div([
        html.Div([
            html.H3("Worst AQI"),
            html.Div(id="worst-aqi")], 
            style={"width": "48%","textAlign": "center"}),

        html.Div([
            html.H3("Best AQI"),
            html.Div(id="best-aqi")], 
            style={"width": "48%","textAlign": "center"})
    ], style={"display": "flex","justifyContent": "space-between","marginTop": "20px"}),

    #--------------------------
    # Pie graph
    #--------------------------
    html.H2("AQI Distribution Across All Available Dates"),
    dcc.Graph(id="aqi-pie-graph",style={"height": "350px"}),


], style={"maxWidth": "1100px","margin": "auto", "padding": "20px"})


#--------------------------
# Callback
#--------------------------
@app.callback(
    Output("daily-average-table", "data"),
    Output("aqi-hourly-graph", "figure"),
    Output("worst-aqi", "children"),
    Output("best-aqi", "children"),
    Output("aqi-pie-graph", "figure"),
    Output("error-message", "children"),

    Input("city-dropdown", "value"),
    Input("date-picker", "date")
)


#--------------------------
# Updating Dashboard
#--------------------------
def update_dashboard(city_id, selected_date):
    #Error if no city or date selected
    if city_id is None or selected_date is None:
        return [], {}, "","",{}, "Please select a city and a date."

    #--------------------------
    # Extracting Pollutants Info
    #--------------------------
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT
                reading_time_utc,
                carbon_monoxide,
                nitric_oxide,
                nitrogen_dioxide,
                ozone,
                sulfur_dioxide,
                fine_particles,
                coarse_particles,
                ammonia,
                aqi
            FROM air_pollution_table
            WHERE city_id = %s
              AND reading_time_utc::date = %s
            ORDER BY reading_time_utc;
        """, (city_id, selected_date))

        rows = cursor.fetchall()
    #--------------------------
    # Extracting Best and Worst AQI Info
    #--------------------------
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT aqi, reading_time_utc
            FROM air_pollution_table
            WHERE city_id = %s
                AND aqi IS NOT NULL
                AND aqi <> 0
            ORDER BY aqi ASC, reading_time_utc ASC
            LIMIT 1;
        """, (city_id,))
        best_aqi, best_date = cursor.fetchone()

        cursor.execute("""
            SELECT aqi, reading_time_utc
            FROM air_pollution_table
            WHERE city_id = %s
                AND aqi IS NOT NULL
                AND aqi <> 0
            ORDER BY aqi DESC, reading_time_utc ASC
            LIMIT 1;
        """, (city_id,))
        worst_aqi, worst_date = cursor.fetchone()

    #--------------------------
    # Extracting Info for Pie Graph
    #--------------------------
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT
                aqi,
                COUNT(*)
            FROM air_pollution_table
            WHERE city_id = %s
            AND aqi IS NOT NULL
            GROUP BY aqi
            ORDER BY aqi;
        """, (city_id,))
        aqi_counts = cursor.fetchall()
    conn.close()

    #--------------------------
    # Creating DF with all pollution variables
    #--------------------------
    df = pd.DataFrame(rows,
    columns=[
        "reading_time_utc",
        "carbon_monoxide",
        "nitric_oxide",
        "nitrogen_dioxide",
        "ozone",
        "sulfur_dioxide",
        "fine_particles",
        "coarse_particles",
        "ammonia",
        "aqi"
    ]
    )  
    #Error message if data is not available
    if df.empty:
        return [], {}, "No data","No data", {},"No data is available for this city and date."
    # Dropping NA's
    df = df.dropna(subset=["aqi"])

    #--------------------------
    # Cnanging the displayed pollutants names
    #--------------------------
    pollutants = [
        "carbon_monoxide",
        "nitrogen_dioxide",
        "ozone",
        "sulfur_dioxide",
        "fine_particles",
        "coarse_particles"
    ]
    pollutant_names = {
        "carbon_monoxide": "CO",
        "nitrogen_dioxide": "NO₂",
        "ozone": "O₃",
        "sulfur_dioxide": "SO₂",
        "fine_particles": "PM2.5",
        "coarse_particles": "PM10"
    }
    #--------------------------
    # Updating the table muth mean values
    #--------------------------
    daily_average = df[pollutants].mean().round(2)
    table_data = [{ "Pollutant": pollutant_names[pollutant],
        "Daily Average": value}for pollutant, value in daily_average.items()]

    #--------------------------
    # Converting times 
    #--------------------------
    df["reading_time_utc"] = pd.to_datetime(df["reading_time_utc"])
    df["hour"] = df["reading_time_utc"].dt.hour
    #Error message if there's unexpected number of observations
    observation_count = (df["reading_time_utc"].dt.hour.nunique())
    if observation_count != 24:
        return [],{},"","",{},f"Incomplete data: only {observation_count} of 24 hourly observations are available."
    hourly_aqi = (df.groupby("hour", as_index=False)["aqi"].mean())


    #--------------------------
    # AQI graph
    #--------------------------
    aqi_count_df = pd.DataFrame(aqi_counts,columns=["aqi", "count"])
    aqi_names = {
        1: "1 - Good",
        2: "2 - Fair",
        3: "3 - Moderate",
        4: "4 - Poor",
        5: "5 - Bad"
    }
    aqi_count_df["category"] = (aqi_count_df["aqi"].map(aqi_names))
    # graph:
    aqi_graph = px.line(
        hourly_aqi,
        x="hour",
        y="aqi",
        markers=True)
    aqi_graph.update_layout(
        xaxis_title="Hour",
        yaxis_title="Air Quality",
        margin={
            "l": 120,
            "r": 20,
            "t": 20,
            "b": 40})
    aqi_graph.update_xaxes(
        range=[0, 23],
        dtick=1)

    aqi_graph.update_yaxes(
        range=[0.8, 5.2],
        tickvals=[1, 2, 3, 4, 5],
        ticktext=[
            "1 - Good",
            "2 - Fair",
            "3 - Moderate",
            "4 - Poor",
            "5 - Bad"])

    
    #--------------------------
    # Worst and Best air-quality hour
    #--------------------------
    best_aqi_text = (f"Best AQI: {best_aqi} | "f"Date: {best_date.strftime('%Y-%m-%d %H:%M')}")
    worst_aqi_text = (f"Worst AQI: {worst_aqi} | "f"Date: {worst_date.strftime('%Y-%m-%d %H:%M')}")

    #--------------------------
    # Pie graph
    #--------------------------
    aqi_pie_graph = px.pie(
        aqi_count_df,
        names="category",
        values="count",
        title="AQI Distribution")
    aqi_pie_graph.update_traces(
        textinfo="percent+label",
        hovertemplate="%{label}<br>Observations: %{value}<extra></extra>")
    aqi_pie_graph.update_layout(
        margin={
            "l": 20,
            "r": 20,
            "t": 50,
            "b": 20})

    #--------------------------
    # Return callback outputs
    #--------------------------
    return table_data, aqi_graph, worst_aqi_text,best_aqi_text,aqi_pie_graph,""


#--------------------------
# Return callback outputs
#--------------------------
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8050,
        debug=True
    )