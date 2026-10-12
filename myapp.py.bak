from dash import Dash, dcc, html, Input, Output, State, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os
import psycopg
from dotenv import load_dotenv
from google import genai
from pathlib import Path


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# DATABASE
# ============================================================

def get_connection():
    return psycopg.connect(
        host=os.getenv("DB_Host"),
        port=os.getenv("DB_Port"),
        dbname=os.getenv("DB_Name"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        sslmode="require"
    )


# ============================================================
# AI CLIENT
# ============================================================

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

MODEL = "gemini-3.6-flash"


def get_ai(prompt):
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt
        )
        return response.text

    except Exception as error:
        error_message = str(error)

        if "429" in error_message or "RESOURCE_EXHAUSTED" in error_message:
            return (
                "I'm temporarily unable to answer because the AI usage limit "
                "has been reached. Please try again later."
            )

        return (
            "I'm sorry, but I'm having trouble connecting to the AI service "
            "right now. Please try again."
        )


# ============================================================
# CITY DATA
# ============================================================

conn = get_connection()

with conn.cursor() as cursor:
    cursor.execute(
        """
        SELECT city_id, city_name, state
        FROM city_table
        ORDER BY city_name;
        """
    )
    cities = cursor.fetchall()

conn.close()


# ============================================================
# APP / ASSETS
# ============================================================

# Keeps your original assets-folder behavior.
# If your assets folder is next to myapp.py instead, replace this section with:
# ASSETS_FOLDER = Path(__file__).resolve().parent / "assets"

PROJECT_ROOT = Path(__file__).resolve().parents[4]
ASSETS_FOLDER = PROJECT_ROOT / "assets"

app = Dash(
    __name__,
    assets_folder=str(ASSETS_FOLDER)
)

app.title = "City Air Tracker"


# ============================================================
# CONSTANTS
# ============================================================

AQI_COLORS = {
    "good": "#24bd68",
    "fair": "#f5b91b",
    "moderate": "#f47b20",
    "poor": "#ed3d4e",
    "very-poor": "#7838e8"
}

AQI_LIGHT_COLORS = {
    "good": "#e8f8ef",
    "fair": "#fff8df",
    "moderate": "#fff0e5",
    "poor": "#fdebed",
    "very-poor": "#f1eafd"
}

AQI_LABELS = {
    1: "1 - Good",
    2: "2 - Fair",
    3: "3 - Moderate",
    4: "4 - Poor",
    5: "5 - Very Poor"
}

AQI_PIE_COLORS = {
    "1 - Good": "#24bd68",
    "2 - Fair": "#f5b91b",
    "3 - Moderate": "#f47b20",
    "4 - Poor": "#ed3d4e",
    "5 - Very Poor": "#7838e8"
}


# ============================================================
# HELPERS
# ============================================================

def classify_aqi(score):
    """
    Converts the averaged 1-5 AQI category score into the closest
    display category.

    1.0 -> Good
    2.0 -> Fair
    3.0 -> Moderate
    4.0 -> Poor
    5.0 -> Very Poor
    """
    if score < 1.5:
        return "Good", "good", "Air quality is good and poses little or no risk."

    if score < 2.5:
        return "Fair", "fair", (
            "Air quality is generally acceptable, with possible minor effects "
            "for sensitive groups."
        )

    if score < 3.5:
        return "Moderate", "moderate", (
            "Sensitive groups may experience some effects."
        )

    if score < 4.5:
        return "Poor", "poor", (
            "Air quality may affect sensitive groups and some members "
            "of the general population."
        )

    return "Very Poor", "very-poor", (
        "Air quality conditions may create a greater health risk."
    )


def display_value(value):
    if value is None or pd.isna(value):
        return "--"
    return f"{float(value):.2f}"


def city_display_name(city_id):
    for city in cities:
        if city[0] == city_id:
            city_name = city[1]
            state = city[2]

            if state:
                return f"{city_name}, {state}"

            return city_name

    return "Selected City"


def empty_figure(message="Select a city and date to view data."):
    fig = go.Figure()

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            visible=False
        ),
        yaxis=dict(
            visible=False
        ),
        annotations=[
            dict(
                text=message,
                x=0.5,
                y=0.5,
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(
                    size=14,
                    color="#7a8996"
                )
            )
        ],
        margin=dict(
            l=20,
            r=20,
            t=20,
            b=20
        )
    )

    return fig


def pollutant_row(symbol, description, value_id):
    return html.Div(
        [
            html.Div(
                [
                    html.Strong(symbol),
                    html.Span(description)
                ],
                className="pollutant-info"
            ),

            html.Div(
                [
                    html.Span(
                        "--",
                        id=value_id,
                        className="pollutant-value"
                    ),
                    html.Span(
                        " μg/m³",
                        className="pollutant-unit"
                    )
                ]
            )
        ],
        className="pollutant-row"
    )


def guide_row(number, title, description, level_class):
    return html.Div(
        [
            html.Div(
                str(number),
                className=f"guide-number {level_class}"
            ),

            html.Div(
                [
                    html.Strong(title),
                    html.Span(description)
                ],
                className="guide-copy"
            )
        ],
        className="guide-row"
    )


def welcome_chat():
    return [
        html.Div(
            [
                html.Strong("Air Tracker AI"),
                dcc.Markdown(
                    "Hi! I'm your Air Tracker assistant. "
                    "Ask me anything about the selected city's air quality."
                )
            ],
            className="chat-message ai-message"
        )
    ]


def render_chat_history(chat_history):
    if not chat_history:
        return welcome_chat()

    chat_display = []

    for message in chat_history:
        role = message.get("role")
        message_text = message.get("message", "")

        if role == "user":
            chat_display.append(
                html.Div(
                    [
                        html.Strong("You"),
                        dcc.Markdown(message_text)
                    ],
                    className="chat-message user-message"
                )
            )
        else:
            chat_display.append(
                html.Div(
                    [
                        html.Strong("Air Tracker AI"),
                        dcc.Markdown(message_text)
                    ],
                    className="chat-message ai-message"
                )
            )

    return chat_display


def make_best_worst_result(aqi_value, reading_time):
    if aqi_value is None or reading_time is None:
        return html.Div(
            "No AQI data available.",
            className="aqi-result"
        )

    numeric_aqi = float(aqi_value)
    label, css_class, _ = classify_aqi(numeric_aqi)

    return html.Div(
        [
            html.Div(
                [
                    html.Span(
                        f"{numeric_aqi:g}",
                        className=f"best-worst-number {css_class}"
                    ),
                    html.Span(
                        label,
                        className=f"best-worst-status {css_class}"
                    )
                ],
                className="best-worst-score"
            ),

            html.Div(
                reading_time.strftime("%B %d, %Y • %I:%M %p"),
                className="best-worst-date"
            )
        ],
        className="aqi-result"
    )


# ============================================================
# REFERENCE TABLE DATA
# ============================================================

REFERENCE_DATA = [
    {
        "quality": "Good",
        "so2": "[0, 20)",
        "no2": "[0, 40)",
        "pm10": "[0, 20)",
        "pm25": "[0, 10)",
        "o3": "[0, 60)",
        "co": "[0, 4400)"
    },
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
    }
]


# ============================================================
# DASH LAYOUT
# ============================================================

app.layout = html.Div(
    [
        html.Div(
            [

                # ====================================================
                # HEADER
                # ====================================================

                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Img(
                                            src=app.get_asset_url("logo2.svg"),
                                            className="logo"
                                        )
                                    ],
                                    className="logo-container"
                                ),

                                html.P(
                                    "Real data. Cleaner tomorrows.",
                                    className="subtitle"
                                )
                            ],
                            className="brand"
                        ),

                        html.Div(
                            [
                                html.A(
                                    "Dashboard",
                                    href="#dashboard"
                                ),
                                html.A(
                                    "Reference",
                                    href="#reference"
                                ),
                                html.A(
                                    "Air Tracker AI",
                                    href="#ai-section"
                                )
                            ],
                            className="nav-links"
                        )
                    ],
                    className="dashboard-header"
                ),

                # ====================================================
                # FILTERS
                # ====================================================

                html.Div(
                    [
                        html.Div(
                            [
                                html.Label("Select a city"),
                                dcc.Dropdown(
                                    id="city-dropdown",
                                    options=[
                                        {
                                            "label": (
                                                f"{city[1]}, {city[2]}"
                                                if city[2]
                                                else city[1]
                                            ),
                                            "value": city[0]
                                        }
                                        for city in cities
                                    ],
                                    placeholder="Choose a city",
                                    clearable=False
                                )
                            ],
                            className="city-selector"
                        ),

                        html.Div(
                            [
                                html.Label("Select a date"),
                                dcc.DatePickerSingle(
                                    id="date-picker",
                                    placeholder="Select a date",
                                    display_format="MMM D, YYYY"
                                )
                            ],
                            className="date-selector"
                        )
                    ],
                    className="filter-card"
                ),

                # ====================================================
                # ERROR / WARNING
                # ====================================================

                html.Div(
                    id="error-message"
                ),

                # ====================================================
                # TOP OVERVIEW
                # ====================================================

                dcc.Loading(type="circle", children=[

                html.Div(
                    [

                        # --------------------------------------------
                        # OVERALL AQI
                        # --------------------------------------------

                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Span("OVERALL AIR QUALITY"),
                                        html.Span(
                                            "ⓘ",
                                            className="info-icon",
                                            title=(
                                                "Overall AQI is the average of "
                                                "the available hourly AQI category "
                                                "values for the selected day."
                                            )
                                        )
                                    ],
                                    className="card-heading-row"
                                ),

                                html.Div(
                                    [
                                        html.Div(
                                            "--",
                                            id="overall-aqi",
                                            className="aqi-number"
                                        ),

                                        html.Div(
                                            "",
                                            id="aqi-status",
                                            className="aqi-status"
                                        )
                                    ],
                                    id="aqi-gauge",
                                    className="aqi-gauge"
                                ),

                                html.P(
                                    "Based on the selected location and date",
                                    id="aqi-description",
                                    className="aqi-description"
                                )
                            ],
                            className="dashboard-card overall-card"
                        ),

                        # --------------------------------------------
                        # POLLUTANTS
                        # --------------------------------------------

                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.H3("Pollutant Levels"),
                                        html.Span(
                                            "Daily Average (μg/m³)",
                                            className="card-caption"
                                        )
                                    ],
                                    className="card-heading-row"
                                ),

                                pollutant_row(
                                    "PM2.5",
                                    "Fine particles",
                                    "pm25-value"
                                ),

                                pollutant_row(
                                    "PM10",
                                    "Coarse particles",
                                    "pm10-value"
                                ),

                                pollutant_row(
                                    "O₃",
                                    "Ozone",
                                    "o3-value"
                                ),

                                pollutant_row(
                                    "NO₂",
                                    "Nitrogen dioxide",
                                    "no2-value"
                                ),

                                pollutant_row(
                                    "SO₂",
                                    "Sulfur dioxide",
                                    "so2-value"
                                ),

                                pollutant_row(
                                    "CO",
                                    "Carbon monoxide",
                                    "co-value"
                                )
                            ],
                            className="dashboard-card pollutant-panel"
                        ),

                        # --------------------------------------------
                        # AQI GUIDE
                        # --------------------------------------------

                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.H3("Air Quality Index Guide"),
                                        html.Span(
                                            "ⓘ",
                                            className="info-icon"
                                        )
                                    ],
                                    className="card-heading-row"
                                ),

                                guide_row(
                                    1,
                                    "Good",
                                    "Minimal health risk",
                                    "good"
                                ),

                                guide_row(
                                    2,
                                    "Fair",
                                    "Minor effects possible for sensitive groups",
                                    "fair"
                                ),

                                guide_row(
                                    3,
                                    "Moderate",
                                    "Possible effects for sensitive groups",
                                    "moderate"
                                ),

                                guide_row(
                                    4,
                                    "Poor",
                                    "May affect everyone",
                                    "poor"
                                ),

                                guide_row(
                                    5,
                                    "Very Poor",
                                    "Greater health risk",
                                    "very-poor"
                                )
                            ],
                            className="dashboard-card guide-panel"
                        )
                    ],
                    className="overview-grid",
                    id="dashboard"
                ),

                # ====================================================
                # HOURLY AQI
                # ====================================================

                html.Div(
                    [
                        html.Div(
                            [
                                html.H3("Average AQI by Hour"),
                                html.Span(
                                    "Hourly air quality conditions",
                                    className="card-caption"
                                )
                            ],
                            className="card-heading-row"
                        ),

                        dcc.Graph(
                            id="aqi-hourly-graph",
                            figure=empty_figure(),
                            config={
                                "displayModeBar": False,
                                "responsive": True
                            },
                            style={
                                "height": "360px"
                            }
                        )
                    ],
                    className="chart-card"
                ),

                # ====================================================
                # BEST / WORST AQI
                # ====================================================

                html.Div(
                    [
                        html.Div(
                            [
                                html.H3("Best Air Quality"),
                                html.Div(
                                    "Select a city",
                                    id="best-aqi",
                                    className="aqi-result"
                                )
                            ],
                            className="aqi-card best-aqi-card"
                        ),

                        html.Div(
                            [
                                html.H3("Worst Air Quality"),
                                html.Div(
                                    "Select a city",
                                    id="worst-aqi",
                                    className="aqi-result"
                                )
                            ],
                            className="aqi-card worst-aqi-card"
                        )
                    ],
                    className="aqi-cards-container"
                ),

                # ====================================================
                # DISTRIBUTION
                # ====================================================

                html.Div(
                    [
                        html.Div(
                            [
                                html.H3(
                                    "AQI Distribution Across All Available Dates"
                                ),
                                html.Span(
                                    "Historical observations",
                                    className="card-caption"
                                )
                            ],
                            className="card-heading-row"
                        ),

                        dcc.Graph(
                            id="aqi-pie-graph",
                            figure=empty_figure(
                                "Select a city to view historical distribution."
                            ),
                            config={
                                "displayModeBar": False,
                                "responsive": True
                            },
                            style={
                                "height": "390px"
                            }
                        )
                    ],
                    className="chart-card"
                ),

                ]),

                # ====================================================
                # REFERENCE TABLES
                # ====================================================

                html.Div(
                    [
                        html.Details(
                            [
                                html.Summary(
                                    "View full pollutant reference tables"
                                ),

                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.H3(
                                                    "Selected Day Averages"
                                                ),

                                                dash_table.DataTable(
                                                    id="daily-average-table",
                                                    columns=[
                                                        {
                                                            "name": "Pollutant",
                                                            "id": "Pollutant"
                                                        },
                                                        {
                                                            "name": "Daily Average",
                                                            "id": "Daily Average"
                                                        }
                                                    ],
                                                    data=[],
                                                    style_cell={
                                                        "textAlign": "center",
                                                        "padding": "9px",
                                                        "fontSize": "12px",
                                                        "fontFamily": (
                                                            "Inter, Arial, sans-serif"
                                                        )
                                                    },
                                                    style_header={
                                                        "fontWeight": "700",
                                                        "backgroundColor": "#f7f9fc"
                                                    }
                                                )
                                            ],
                                            className="reference-table-block"
                                        ),

                                        html.Div(
                                            [
                                                html.H3(
                                                    "AQ Components Reference"
                                                ),

                                                dash_table.DataTable(
                                                    columns=[
                                                        {
                                                            "name": [
                                                                "",
                                                                "Qualitative name"
                                                            ],
                                                            "id": "quality"
                                                        },
                                                        {
                                                            "name": [
                                                                (
                                                                    "Pollutant "
                                                                    "concentration "
                                                                    "in μg/m³"
                                                                ),
                                                                "SO₂"
                                                            ],
                                                            "id": "so2"
                                                        },
                                                        {
                                                            "name": [
                                                                (
                                                                    "Pollutant "
                                                                    "concentration "
                                                                    "in μg/m³"
                                                                ),
                                                                "NO₂"
                                                            ],
                                                            "id": "no2"
                                                        },
                                                        {
                                                            "name": [
                                                                (
                                                                    "Pollutant "
                                                                    "concentration "
                                                                    "in μg/m³"
                                                                ),
                                                                "PM10"
                                                            ],
                                                            "id": "pm10"
                                                        },
                                                        {
                                                            "name": [
                                                                (
                                                                    "Pollutant "
                                                                    "concentration "
                                                                    "in μg/m³"
                                                                ),
                                                                "PM2.5"
                                                            ],
                                                            "id": "pm25"
                                                        },
                                                        {
                                                            "name": [
                                                                (
                                                                    "Pollutant "
                                                                    "concentration "
                                                                    "in μg/m³"
                                                                ),
                                                                "O₃"
                                                            ],
                                                            "id": "o3"
                                                        },
                                                        {
                                                            "name": [
                                                                (
                                                                    "Pollutant "
                                                                    "concentration "
                                                                    "in μg/m³"
                                                                ),
                                                                "CO"
                                                            ],
                                                            "id": "co"
                                                        }
                                                    ],
                                                    data=REFERENCE_DATA,
                                                    merge_duplicate_headers=True,
                                                    style_cell={
                                                        "textAlign": "center",
                                                        "padding": "8px",
                                                        "fontSize": "11px",
                                                        "fontFamily": (
                                                            "Inter, Arial, sans-serif"
                                                        ),
                                                        "whiteSpace": "normal",
                                                        "height": "auto"
                                                    },
                                                    style_header={
                                                        "fontWeight": "700",
                                                        "backgroundColor": "#f7f9fc"
                                                    }
                                                )
                                            ],
                                            className="reference-table-block"
                                        )
                                    ],
                                    className="reference-tables-grid"
                                )
                            ],
                            className="reference-details",
                            id="reference"
                        )
                    ],
                    className="dashboard-card reference-card"
                ),

                # ====================================================
                # AIR TRACKER AI
                # ====================================================

                html.Div(
                    [
                        html.H2("Ask Air Tracker AI"),

                        html.P(
                            "Ask questions about the selected city's air quality."
                        ),

                        dcc.Store(
                            id="ai-chat-history",
                            data=[]
                        ),

                        html.Div(
                            welcome_chat(),
                            id="ai-chat-history-display"
                        ),

                        html.Div(
                            [
                                dcc.Input(
                                    id="ai-question",
                                    type="text",
                                    placeholder="Ask about the air quality...",
                                    debounce=False
                                ),

                                html.Button(
                                    "Ask",
                                    id="ai-button",
                                    n_clicks=0
                                )
                            ],
                            className="chat-input-row"
                        )
                    ],
                    className="ai-assistant",
                    id="ai-section"
                )
            ],
            className="page-container"
        )
    ],
    className="app-shell"
)


# ============================================================
# DASHBOARD CALLBACK
# ============================================================

@app.callback(
    Output("daily-average-table", "data"),
    Output("aqi-hourly-graph", "figure"),
    Output("overall-aqi", "children"),
    Output("aqi-status", "children"),
    Output("aqi-description", "children"),
    Output("aqi-gauge", "className"),
    Output("aqi-status", "className"),
    Output("pm25-value", "children"),
    Output("pm10-value", "children"),
    Output("o3-value", "children"),
    Output("no2-value", "children"),
    Output("so2-value", "children"),
    Output("co-value", "children"),
    Output("best-aqi", "children"),
    Output("worst-aqi", "children"),
    Output("aqi-pie-graph", "figure"),
    Output("error-message", "children"),
    Input("city-dropdown", "value"),
    Input("date-picker", "date")
)
def update_dashboard(city_id, selected_date):

    # --------------------------------------------------------
    # NO SELECTION
    # --------------------------------------------------------

    if city_id is None or selected_date is None:
        return (
            [],
            empty_figure(),
            "--",
            "",
            "",
            "aqi-gauge",
            "aqi-status",
            "--",
            "--",
            "--",
            "--",
            "--",
            "--",
            "Select a city",
            "Select a city",
            empty_figure(
                "Select a city to view historical distribution."
            ),
            ""
        )

    # --------------------------------------------------------
    # QUERY SELECTED DAY
    # --------------------------------------------------------

    conn = get_connection()

    with conn.cursor() as cursor:
        cursor.execute(
            """
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
            """,
            (city_id, selected_date)
        )

        rows = cursor.fetchall()

    # --------------------------------------------------------
    # BEST AQI
    # --------------------------------------------------------

    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT aqi, reading_time_utc
            FROM air_pollution_table
            WHERE city_id = %s
              AND aqi IS NOT NULL
              AND aqi <> 0
            ORDER BY aqi ASC, reading_time_utc ASC
            LIMIT 1;
            """,
            (city_id,)
        )

        best_result = cursor.fetchone()

    # --------------------------------------------------------
    # WORST AQI
    # --------------------------------------------------------

    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT aqi, reading_time_utc
            FROM air_pollution_table
            WHERE city_id = %s
              AND aqi IS NOT NULL
              AND aqi <> 0
            ORDER BY aqi DESC, reading_time_utc ASC
            LIMIT 1;
            """,
            (city_id,)
        )

        worst_result = cursor.fetchone()

    # --------------------------------------------------------
    # HISTORICAL DISTRIBUTION
    # --------------------------------------------------------

    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                aqi,
                COUNT(*)
            FROM air_pollution_table
            WHERE city_id = %s
              AND aqi IS NOT NULL
            GROUP BY aqi
            ORDER BY aqi;
            """,
            (city_id,)
        )

        aqi_counts = cursor.fetchall()

    conn.close()

    # --------------------------------------------------------
    # BUILD DATAFRAME
    # --------------------------------------------------------

    df = pd.DataFrame(
        rows,
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

    # --------------------------------------------------------
    # NO DATA FOR DATE
    # --------------------------------------------------------

    if df.empty:
        return (
            [],
            empty_figure(
                "No data is available for this city and date."
            ),
            "--",
            "No data",
            "No data is available for the selected date.",
            "aqi-gauge",
            "aqi-status",
            "--",
            "--",
            "--",
            "--",
            "--",
            "--",
            (
                make_best_worst_result(*best_result)
                if best_result
                else "No data"
            ),
            (
                make_best_worst_result(*worst_result)
                if worst_result
                else "No data"
            ),
            empty_figure(
                "Historical data is unavailable."
            ),
            "No data is available for this city and date."
        )

    df["aqi"] = pd.to_numeric(
        df["aqi"],
        errors="coerce"
    )

    df = df.dropna(
        subset=["aqi"]
    )

    if df.empty:
        return (
            [],
            empty_figure(
                "AQI values are unavailable for this date."
            ),
            "--",
            "No AQI data",
            "AQI values are unavailable for the selected date.",
            "aqi-gauge",
            "aqi-status",
            "--",
            "--",
            "--",
            "--",
            "--",
            "--",
            (
                make_best_worst_result(*best_result)
                if best_result
                else "No data"
            ),
            (
                make_best_worst_result(*worst_result)
                if worst_result
                else "No data"
            ),
            empty_figure(
                "Historical AQI data is unavailable."
            ),
            "AQI values are unavailable for this city and date."
        )

    # --------------------------------------------------------
    # POLLUTANT AVERAGES
    # --------------------------------------------------------

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

    for pollutant in pollutants:
        df[pollutant] = pd.to_numeric(
            df[pollutant],
            errors="coerce"
        )

    daily_average = (
        df[pollutants]
        .mean()
        .round(2)
    )

    table_data = [
        {
            "Pollutant": pollutant_names[pollutant],
            "Daily Average": display_value(value)
        }
        for pollutant, value in daily_average.items()
    ]

    # --------------------------------------------------------
    # OVERALL AQI
    # --------------------------------------------------------

    overall_aqi = round(
        float(df["aqi"].mean()),
        2
    )

    aqi_status, aqi_class, aqi_description = classify_aqi(
        overall_aqi
    )

    gauge_class = f"aqi-gauge {aqi_class}"
    status_class = f"aqi-status {aqi_class}"

    # --------------------------------------------------------
    # TIME CONVERSION
    # --------------------------------------------------------

    df["reading_time_utc"] = pd.to_datetime(
        df["reading_time_utc"]
    )

    df["hour"] = (
        df["reading_time_utc"]
        .dt.hour
    )

    observation_count = (
        df["hour"]
        .nunique()
    )

    warning_message = ""

    if observation_count != 24:
        warning_message = (
            f"Incomplete data: {observation_count} of 24 hourly "
            "observations are available."
        )

    # --------------------------------------------------------
    # HOURLY AQI DATA
    # --------------------------------------------------------

    hourly_aqi = (
        df.groupby(
            "hour",
            as_index=False
        )["aqi"]
        .mean()
    )

    # --------------------------------------------------------
    # HOURLY AQI GRAPH
    # --------------------------------------------------------

    line_color = AQI_COLORS.get(
        aqi_class,
        "#24bd68"
    )

    aqi_graph = px.line(
        hourly_aqi,
        x="hour",
        y="aqi",
        markers=True
    )

    aqi_graph.update_traces(
        line=dict(
            width=3,
            color=line_color
        ),
        marker=dict(
            size=7,
            color=line_color
        ),
        fill="tozeroy",
        fillcolor="rgba(36, 189, 104, 0.07)",
        hovertemplate=(
            "<b>Hour %{x}</b><br>"
            "AQI: %{y:.2f}"
            "<extra></extra>"
        )
    )

    # AQI category background bands
    aqi_graph.add_hrect(
        y0=0.5,
        y1=1.5,
        fillcolor="#dcf7e7",
        opacity=0.75,
        line_width=0,
        layer="below"
    )

    aqi_graph.add_hrect(
        y0=1.5,
        y1=2.5,
        fillcolor="#fff7d6",
        opacity=0.75,
        line_width=0,
        layer="below"
    )

    aqi_graph.add_hrect(
        y0=2.5,
        y1=3.5,
        fillcolor="#ffead8",
        opacity=0.75,
        line_width=0,
        layer="below"
    )

    aqi_graph.add_hrect(
        y0=3.5,
        y1=4.5,
        fillcolor="#fde1e4",
        opacity=0.75,
        line_width=0,
        layer="below"
    )

    aqi_graph.add_hrect(
        y0=4.5,
        y1=5.5,
        fillcolor="#eee5fc",
        opacity=0.75,
        line_width=0,
        layer="below"
    )

    aqi_graph.update_layout(
        title=None,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(
            l=65,
            r=20,
            t=10,
            b=45
        ),
        hovermode="x unified",
        font=dict(
            family="Inter, Arial, sans-serif",
            color="#67758b",
            size=12
        )
    )

    aqi_graph.update_xaxes(
        range=[0, 23],
        tickvals=[
            0, 3, 6, 9,
            12, 15, 18, 21
        ],
        ticktext=[
            "12 AM",
            "3 AM",
            "6 AM",
            "9 AM",
            "12 PM",
            "3 PM",
            "6 PM",
            "9 PM"
        ],
        showgrid=False,
        zeroline=False,
        title=None
    )

    aqi_graph.update_yaxes(
        range=[0.5, 5.5],
        tickvals=[
            1, 2, 3, 4, 5
        ],
        ticktext=[
            "Good",
            "Fair",
            "Moderate",
            "Poor",
            "Very Poor"
        ],
        showgrid=True,
        gridcolor="rgba(255,255,255,0.85)",
        zeroline=False,
        title=None
    )

    # --------------------------------------------------------
    # BEST / WORST
    # --------------------------------------------------------

    if best_result is not None:
        best_aqi_content = make_best_worst_result(
            best_result[0],
            best_result[1]
        )
    else:
        best_aqi_content = "No best AQI data available."

    if worst_result is not None:
        worst_aqi_content = make_best_worst_result(
            worst_result[0],
            worst_result[1]
        )
    else:
        worst_aqi_content = "No worst AQI data available."

    # --------------------------------------------------------
    # HISTORICAL AQI DISTRIBUTION
    # --------------------------------------------------------

    aqi_count_df = pd.DataFrame(
        aqi_counts,
        columns=[
            "aqi",
            "count"
        ]
    )

    if not aqi_count_df.empty:
        aqi_count_df["aqi"] = pd.to_numeric(
            aqi_count_df["aqi"],
            errors="coerce"
        )

        aqi_count_df["category"] = (
            aqi_count_df["aqi"]
            .map(AQI_LABELS)
        )

        aqi_count_df = aqi_count_df.dropna(
            subset=["category"]
        )

    if aqi_count_df.empty:
        aqi_pie_graph = empty_figure(
            "Historical AQI distribution is unavailable."
        )

    else:
        aqi_pie_graph = px.pie(
            aqi_count_df,
            names="category",
            values="count",
            hole=0.62,
            color="category",
            color_discrete_map=AQI_PIE_COLORS,
            category_orders={
                "category": [
                    "1 - Good",
                    "2 - Fair",
                    "3 - Moderate",
                    "4 - Poor",
                    "5 - Very Poor"
                ]
            }
        )

        aqi_pie_graph.update_traces(
            textinfo="none",
            hovertemplate=(
                "<b>%{label}</b><br>"
                "%{percent}<br>"
                "%{value} observations"
                "<extra></extra>"
            ),
            marker=dict(
                line=dict(
                    color="white",
                    width=2
                )
            )
        )

        aqi_pie_graph.update_layout(
            title=None,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(
                l=20,
                r=20,
                t=15,
                b=20
            ),
            legend=dict(
                orientation="v",
                x=1.02,
                y=0.5,
                yanchor="middle",
                font=dict(
                    size=12
                )
            ),
            font=dict(
                family="Inter, Arial, sans-serif",
                color="#67758b"
            ),
            annotations=[
                dict(
                    text="Total<br>Observations",
                    x=0.5,
                    y=0.5,
                    showarrow=False,
                    font=dict(
                        size=14,
                        color="#10213d"
                    )
                )
            ]
        )

    # --------------------------------------------------------
    # RETURN
    # --------------------------------------------------------

    return (
        table_data,
        aqi_graph,
        display_value(overall_aqi),
        aqi_status,
        aqi_description,
        gauge_class,
        status_class,
        display_value(daily_average["fine_particles"]),
        display_value(daily_average["coarse_particles"]),
        display_value(daily_average["ozone"]),
        display_value(daily_average["nitrogen_dioxide"]),
        display_value(daily_average["sulfur_dioxide"]),
        display_value(daily_average["carbon_monoxide"]),
        best_aqi_content,
        worst_aqi_content,
        aqi_pie_graph,
        warning_message
    )


# ============================================================
# AIR TRACKER AI CALLBACK
# ============================================================

@app.callback(
    Output("ai-chat-history-display", "children"),
    Output("ai-chat-history", "data"),
    Output("ai-question", "value"),
    Input("ai-button", "n_clicks"),
    State("ai-question", "value"),
    State("city-dropdown", "value"),
    State("date-picker", "date"),
    State("ai-chat-history", "data")
)
def update_ai_chat(
    n_clicks,
    question,
    city_id,
    selected_date,
    chat_history
):

    if chat_history is None:
        chat_history = []

    # --------------------------------------------------------
    # INITIAL WELCOME
    # --------------------------------------------------------

    if not n_clicks:
        return (
            render_chat_history(chat_history),
            chat_history,
            ""
        )

    # --------------------------------------------------------
    # EMPTY QUESTION
    # --------------------------------------------------------

    if not question or not question.strip():
        return (
            render_chat_history(chat_history),
            chat_history,
            ""
        )

    # --------------------------------------------------------
    # CITY / DATE REQUIRED
    # --------------------------------------------------------

    if city_id is None or selected_date is None:
        display = render_chat_history(chat_history)

        display.append(
            html.Div(
                "Please select a city and date before asking "
                "Air Tracker AI a question.",
                className="chat-error"
            )
        )

        return (
            display,
            chat_history,
            ""
        )

    city_name = city_display_name(
        city_id
    )

    # --------------------------------------------------------
    # FETCH DATA FOR AI CONTEXT
    # --------------------------------------------------------

    conn = get_connection()

    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                carbon_monoxide,
                nitrogen_dioxide,
                ozone,
                sulfur_dioxide,
                fine_particles,
                coarse_particles,
                aqi
            FROM air_pollution_table
            WHERE city_id = %s
              AND reading_time_utc::date = %s
            ORDER BY reading_time_utc;
            """,
            (city_id, selected_date)
        )

        readings = cursor.fetchall()

    conn.close()

    if not readings:
        display = render_chat_history(
            chat_history
        )

        display.append(
            html.Div(
                "There is no air quality data available for "
                "this city and date.",
                className="chat-error"
            )
        )

        return (
            display,
            chat_history,
            ""
        )

    # --------------------------------------------------------
    # CALCULATE AI CONTEXT
    # --------------------------------------------------------

    data = pd.DataFrame(
        readings,
        columns=[
            "carbon_monoxide",
            "nitrogen_dioxide",
            "ozone",
            "sulfur_dioxide",
            "fine_particles",
            "coarse_particles",
            "aqi"
        ]
    )

    numeric_columns = [
        "carbon_monoxide",
        "nitrogen_dioxide",
        "ozone",
        "sulfur_dioxide",
        "fine_particles",
        "coarse_particles",
        "aqi"
    ]

    for column in numeric_columns:
        data[column] = pd.to_numeric(
            data[column],
            errors="coerce"
        )

    pollutant_columns = [
        "carbon_monoxide",
        "nitrogen_dioxide",
        "ozone",
        "sulfur_dioxide",
        "fine_particles",
        "coarse_particles"
    ]

    daily_average = (
        data[pollutant_columns]
        .mean()
        .round(2)
    )

    overall_aqi = round(
        float(data["aqi"].mean()),
        2
    )

    # --------------------------------------------------------
    # PREVIOUS CONVERSATION
    # --------------------------------------------------------

    conversation = ""

    for message in chat_history:
        conversation += (
            f'{message["role"]}: '
            f'{message["message"]}\n'
        )

    # --------------------------------------------------------
    # AI PROMPT
    # --------------------------------------------------------

    prompt = f"""
You are Air Tracker AI, a conversational assistant for the City Air Tracker dashboard.

Your job is to help users understand air quality data and use that information at their own discretion.

City: {city_name}

Date: {selected_date}

Overall AQI category score: {overall_aqi}

Pollutant averages in μg/m³:

PM2.5: {display_value(daily_average["fine_particles"])}

PM10: {display_value(daily_average["coarse_particles"])}

O3: {display_value(daily_average["ozone"])}

NO2: {display_value(daily_average["nitrogen_dioxide"])}

SO2: {display_value(daily_average["sulfur_dioxide"])}

CO: {display_value(daily_average["carbon_monoxide"])}

Previous conversation:

{conversation}

User question:

{question}

Answer the user's question using the air quality data above.

Be conversational and helpful.

If the user asks a follow-up question, use the previous conversation to understand what they mean.

Do not make up air quality measurements that are not provided.

If you don't know, simply say you don't know.

Do not use LaTeX or mathematical notation.

Use normal names such as O3, NO2, SO2, PM2.5, PM10, and CO.

Use simple Markdown when helpful.

For health-related questions, provide general information only.

Do not diagnose medical conditions or claim to provide medical advice.

If the available data is not enough to answer the question, clearly say that.

If the user asks a question that is inappropriate, redirect them to the questions you can answer.

If they keep insisting, end the conversation.
"""

    ai_response = get_ai(
        prompt
    )

    # --------------------------------------------------------
    # SAVE CONVERSATION
    # --------------------------------------------------------

    chat_history.append(
        {
            "role": "user",
            "message": question.strip()
        }
    )

    chat_history.append(
        {
            "role": "assistant",
            "message": ai_response
        }
    )

    return (
        render_chat_history(chat_history),
        chat_history,
        ""
    )


# ============================================================
# RUN APP
# ============================================================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(
            os.getenv(
                "PORT",
                8050
            )
        ),
        debug=False
    )
