from pydoc import classname
from click import style
import pandas as pd
import numpy as np

import dash

from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc

import altair as alt
from vega_datasets import data as datasets

app = dash.Dash(__name__)

# server = app.server

# Load data
gapminder = pd.read_csv(
    "data/processed/gapminder_processed.csv", parse_dates=["year"]
)

# create clean country list
country_list = gapminder[["name", "id"]].drop_duplicates()

# Define helper code

"""Options"""
# Selection filter options - Years
opt_dropdown_years = [
    {"label": year, "value": year}
    for year in np.unique(gapminder["year"].dt.year)
]
# Selection filter options - Region
opt_radio_regions = [{"label": "All", "value": "All"}] + [
    {"label": region, "value": region}
    for region in np.unique(gapminder["region"])
]

# Selection filter options - Target of the study
opt_dropdown_targets = [
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
    for country in np.unique(gapminder["country"])
]

""" Layouts """

filter_panel = [
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
        options=opt_dropdown_targets,
        className="dropdown",
    ),
    html.Br(),
    dcc.Dropdown(
        id="target_input_x",
        value="income",
        options=opt_dropdown_targets,
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
]

plot_body = [
    dbc.Row(
        [
            ### Top row images go here
            dbc.Col(
                [
                    ### Plot 1
                    html.H2("Life Expectancy world map"),
                    html.Iframe(
                        id="world_map",
                        className="world-map",
                    ),
                ],
                className="col",
            ),
            dbc.Col(
                [
                    ### Plot 2 goes here
                    html.H2("Top 10 countries"),
                ],
            ),
        ],
        className="row",
    ),
    dbc.Row(
        [
            ### Second row plots go here
            dbc.Col(
                [
                    ### Plot 3
                    html.H2("Life Expectancy during the time chart"),
                    html.Iframe(
                        id="line_plot",
                        className="line-plot",
                        style={"width":"110%", "height" : "350px"}
                    ),
                ],
                className="col",
            ),
            dbc.Col(
                [
                    ### Plot 4 goes here
                    html.H2("Life expectancy vs GDP Plot"),
                    html.Iframe(id="bubble_plot", className="bubble-plot"),
                ],
            ),
        ],
        className="row",
    ),
]

# Define page layout
page_layout = html.Div(
    className="page_layout",
    children=[
        dbc.Col(filter_panel, className="panel"),
        dbc.Col(plot_body, className="body"),
    ],
)


# Overall layout
app.layout = html.Div(id="main", className="app", children=page_layout)

# Set up callbacks/backend
@app.callback(
    Output("bubble_plot", "srcDoc"),
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
        idx = np.where((gapminder["year"].dt.year == year))
    else:
        idx = np.where(
            (gapminder["year"].dt.year == year)
            & (gapminder["region"] == region)
        )

    gap_filtered = gapminder.loc[idx]

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


# Set up callbacks/backend
@app.callback(
    Output("world_map", "srcDoc"),
    Input("target_input_y", "value"),
    Input("region_input", "value"),
)
def plot_map(target, region):
    """
    Create map plot for statsitic of interested based on selected filters
    Parameters
    --------
    target: string
        Selection from target of interest filter
    region: string
        Selection from the Region filter
    Returns
    --------
    map_chart
        map chart showing target of interest for specific region
    Example
    --------
    > plot_map("Asia", "life_expectany")
    """
    alt.data_transformers.disable_max_rows()

    data = gapminder[(gapminder["region"] == region)]

    # append clean country list
    if region == "All":
        data = data.merge(country_list, how="outer", on=["name", "id"])

    # replace NaN values with 0
    data[[target]] = data[[target]].fillna(-1)

    # create world_map
    world_map = alt.topo_feature(datasets.world_110m.url, "countries")

    background = alt.Chart(world_map).mark_geoshape(
        fill="lightgray", stroke="white"
    )

    map_chart = (
        alt.Chart(world_map, title=f"{target} by Country for")
        .mark_geoshape(stroke="black")
        .transform_lookup(
            lookup="id",
            from_=alt.LookupData(data, key="id", fields=["name", target]),
        )
        .encode(
            tooltip=["name:O", target + ":Q"],
            color=alt.Color(target + ":Q", title=f"{target}"),
        )
    )

    final_map = (
        (background + map_chart)
        .configure_view(strokeWidth=0)
        .properties(width=450, height=350)
        .project("naturalEarth1")
    )

    return final_map.to_html()


# Set up callbacks/backend
@app.callback(
    Output("line_plot", "srcDoc"),
    Input("target_input_y", "value"),
    Input("region_input", "value"),
    Input("country_input", "value"),
    Input("year_input", "value"),
)
def plot_line(target, region, country,  year):
    """
    Create line plot for statsitic of interested based on selected filters
    Parameters
    --------
    target: string
        Selection from target of interest filter
    region: string
        Selection from the Region filter
    year : int
        Selection from the year dropdown
    Returns
    --------
    line_chart
        line chart showing target of interest for specific region
    Example
    --------
    > plot_line("life_expectany", "Asia", "Afghanistan", 1970 )
    """

    pd.options.mode.chained_assignment = None  # default='warn'
    gm_country = gapminder[gapminder['country'] == country]
    df = gm_country[["year", target]]

    if(region == "All"):
        gm_region = gapminder
    else:
        gm_region = gapminder[gapminder['sub_region'] == region]
    df.loc[:,region]=gm_region.groupby(['year']).mean().reset_index()[target]

    df.loc[:,"Whole world"]=gapminder.groupby(['year']).mean().reset_index()[target]
    df = df.query(f"year <= {year}")

    df.rename(columns={target: country}, inplace=True)

    df = pd.melt(df, id_vars=['year'], value_vars=[country,region,'Whole world'])
    df = df.astype({"variable": str}, errors='raise') 
    df["value"] = pd.to_numeric(df["value"])


    line_chart= alt.Chart(df).mark_line().encode(
        x='year',
        y='value',
        color = 'variable'
    ).properties(width=250, height=250)
    return line_chart.to_html()


if __name__ == "__main__":
    app.run_server(debug=True)
