import pandas as pd
import numpy as np

import dash

from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc

import altair as alt

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
# server = app.server

# Load data
# Data link to be changed to local csv file in data/raw folder
# gap_url = 'https://raw.githubusercontent.com/UofTCoders/workshops-dc-py/master/data/processed/world-data-gapminder.csv'
gap = pd.read_csv("data/raw/gapminder_2018.csv", parse_dates=["year"])

# Define helper code

# Selection filter options - Years
opt_dropdown_years = [
    {"label": year, "value": year} for year in np.unique(gap["year"].dt.year)
]
# Selection filter options - Region
opt_radio_regions = [{"label": "All", "value": "All"}] + [
    {"label": region, "value": region} for region in np.unique(gap["region"])
]

# Selection filter options - Target of the study - Y-axis of the plots
# TBD - Other options to be added
opt_dropdown_target_y = [
    {"label": "Population", "value": "population"},
    {"label": "Income Group", "value": "income_group"},
    {"label": "GDP", "value": "income"},
    {"label": "Life Expectancy", "value": "life_expectancy"},
    {"label": "Children per woman", "value": "children_per_woman"},
    {"label": "Child Mortality", "value": "child_mortality"},
    {"label": "Population density", "value": "pop_density"},
    {"label": "CO2 per capita", "value": "co2_per_capita"},
    {"label": "Avg years in school (men)", "value": "years_in_school_men"},
    {"label": "Avg years in school (men)", "value": "years_in_school_women"},
]

# Selection filter options - Target of the study - X-axis of the plots
# TBD - Other options to be added
opt_dropdown_target_x = [
    {"label": "Population", "value": "population"},
    {"label": "Income Group", "value": "income_group"},
    {"label": "GDP", "value": "income"},
    {"label": "Life Expectancy", "value": "life_expectancy"},
    {"label": "Children per woman", "value": "children_per_woman"},
    {"label": "Child Mortality", "value": "child_mortality"},
    {"label": "Population density", "value": "pop_density"},
    {"label": "CO2 per capita", "value": "co2_per_capita"},
    {"label": "Avg years in school (men)", "value": "years_in_school_men"},
    {"label": "Avg years in school (men)", "value": "years_in_school_women"},
]

# Selection filter country
opt_dropdown_country = [
    {"label": country, "value": country}
    for country in np.unique(gap["country"])
]

# Define page layout
page_layout = [
    dbc.Container(
        [
            dbc.Row(
                [
                    ## one third left criteria selection bar
                    dbc.Col(
                        [
                            ### Top Header Text
                            html.H2("Gapminder Dashboard"),
                            html.Br(),
                            html.Br(),
                            #### Add LHS selection filters here
                            html.H3("Filters", className="text-primary"),
                            html.H5("Target of Study", className="text-dark"),
                            dcc.Dropdown(
                                id="target_input_y",
                                value="life_expectancy",
                                options=opt_dropdown_target_y,
                                className="dropdown",
                            ),
                            html.Br(),
                            dcc.Dropdown(
                                id="target_input_x",
                                value="income",
                                options=opt_dropdown_target_x,
                                className="dropdown",
                            ),
                            html.Br(),
                            html.H5("Country", className="text-dark"),
                            dcc.Dropdown(
                                id="country_input",
                                value="Afghanistan",
                                options=opt_dropdown_country,
                                className="dropdown",
                            ),
                            html.H5("Region", className="text-dark"),
                            dcc.RadioItems(
                                id="region_input",
                                value="All",
                                options=opt_radio_regions,
                                className="radio",
                            ),
                            html.Br(),
                            html.H5("Year", className="text-dark"),
                            dcc.Dropdown(
                                id="year_input",
                                value=1970,
                                options=opt_dropdown_years,
                                className="dropdown",
                            ),
                        ],
                        width="4",
                        className="one_third_col_left_selection",
                    ),
                    ## two thirds main plots area
                    dbc.Col(
                        [
                            dbc.Row(
                                [
                                    ### Top row images go here
                                    dbc.Col(
                                        [
                                            ### Plot 1
                                            html.H2(
                                                "Life Expectancy world map"
                                            )
                                        ]
                                    ),
                                    dbc.Col(
                                        [
                                            ### Plot 2 goes here
                                            html.H2("Top 10 countries"),
                                        ]
                                    ),
                                ]
                            ),
                            dbc.Row(
                                [
                                    ### Second row plots go here
                                    dbc.Col(
                                        [
                                            ### Plot 3
                                            html.H2(
                                                "Life Expectancy during the time chart"
                                            ),
                                        ],
                                        width="4",
                                    ),
                                    dbc.Col(
                                        [
                                            ### Plot 4 goes here
                                            html.H2(
                                                "Life expectancy vs GDP Plot"
                                            ),
                                            html.Iframe(
                                                id="scatter",
                                                style={
                                                    "border-width": "0px",
                                                    "width": "100%",
                                                    "height": "500px",
                                                },
                                            ),
                                        ],
                                        width="4",
                                    ),
                                ]
                            ),
                        ],
                        width="8",
                        className="two_third_main_display",
                    ),
                ]
            )
        ],
        fluid=True,
    )
]

# Overall layout
app.layout = html.Div(id="main", children=page_layout)

# Set up callbacks/backend
@app.callback(
    Output("scatter", "srcDoc"),
    Input("year_input", "value"),
    Input("region_input", "value"),
    Input("target_input_y", "value"),
    Input("target_input_x", "value"),
)
def plot_lifeexp_gdp(year, region, target_y, target_x):
    # Define plot label depending on target
    # TBD - Other options to be added
    if target_y == "life_expectancy":
        ylabel = "Life Expectancy"

    # Filter dataframe depending on year and region choice
    # If region == 'All', then only filter on year, else filter on both year and region
    if region == "All":
        idx = np.where((gap["year"].dt.year == year))
    else:
        idx = np.where(
            (gap["year"].dt.year == year) & (gap["region"] == region)
        )

    gap_filtered = gap.loc[idx]

    scatter_pop_lifeexp = (
        alt.Chart(gap_filtered)
        .mark_circle()
        .encode(
            x=alt.X(target_x, title=target_x),
            y=alt.Y(target_y, title=target_y),
            color="region",
            size="population",
        )
        .properties(width=250, height=250)
    )
    return scatter_pop_lifeexp.to_html()


if __name__ == "__main__":
    app.run_server(debug=True)
