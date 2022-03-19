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
app.title = "Gapminder Dashboard"

server = app.server

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
opt_radio_regions = [
    {"label": region, "value": region}
    for region in np.unique(gapminder["region"])
] + [{"label": "All", "value": "All"}]

# Selection filter options - Target of the study
opt_dropdown_targets = [
    {"label": "Population", "value": "population"},
    {"label": "GDP", "value": "income"},
    {"label": "Life Expectancy", "value": "life_expectancy"},
    {"label": "Children per woman", "value": "children_per_woman"},
    {"label": "Child Mortality", "value": "child_mortality"},
    {"label": "Population density", "value": "pop_density"},
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
    html.H3("Filters"),
    html.H4("Target of Study"),
    dcc.Dropdown(
        id="target_input_y",
        value="life_expectancy",
        options=opt_dropdown_targets,
        className="dropdown",
        clearable=False,
    ),
    html.Br(),
    dcc.Dropdown(
        id="target_input_x",
        value="income",
        options=opt_dropdown_targets,
        className="dropdown",
        clearable=False,
    ),
    html.H5("Interpretation of Target of Study:"),
    html.H5("- Population is number of people living"),
    html.H5("- Income is GDP per capita adjusted for purchasing power"),
    html.H5("- Children per Woman is the number of children born to each woman"),
    html.H5("- Child Mortality is deaths of children under 5 years per 1000 live births"),
    html.H5("- Population Density is average number of people per km2"),
    html.H4("Region"),
    dcc.RadioItems(
        id="region_input",
        value="Africa",
        options=opt_radio_regions,
        className="radio",
    ),
    html.Br(),
    html.H4("Country"),
    dcc.Dropdown(
        id="country_input",
        value="Angola",
        className="dropdown",
        clearable=False,
    ),
    html.Br(),
    html.H4("Year"),
    dcc.Slider(
        id="year_input",
        min=1950,
        max=2018,
        step=1,
        value=1970,
        marks={1950: "1950", 2018: "2018"},
        included=False,
        tooltip={"placement": "bottom", "always_visible": True},
    ),
]

plot_body = [
    dbc.Row(
        [
            dbc.Col(
                [
                    html.Iframe(
                        id="world_map",
                        className="plot",
                    ),
                ],
                className="world-map",
            ),
            dbc.Col(
                [
                    # html.H3("Top 10 countries in the region"),
                    html.Iframe(
                        id="top_count_bar_plot",
                        className="plot",
                    ),
                ],
                className="bar-plot",
            ),
        ],
        className="top-row",
    ),
    dbc.Row(
        [
            dbc.Col(
                [
                    # html.H3("Target of study over time"),
                    html.Iframe(
                        id="line_plot",
                        className="plot",
                    ),
                ],
                className="line-plot",
            ),
            dbc.Col(
                [
                    # html.H3("Target 1 vs Target 2"),
                    html.Iframe(id="bubble_plot", className="plot"),
                ],
                className="bubble-plot",
            ),
        ],
        className="bottom-row",
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


# Set up callback for bar-chart
@app.callback(
    Output("country_input", "options"), Input("region_input", "value")
)
def sync_filters(selected_region):
    """
    Sync continents and countries in filter
    """
    if selected_region == "All":
        valid_countries = gapminder["country"].unique()
    else:
        valid_countries = gapminder.query("region == @selected_region")[
            "country"
        ].unique()
    country_options = [{"label": col, "value": col} for col in valid_countries]
    return country_options


# Set up callback for bar-chart
@app.callback(
    Output("top_count_bar_plot", "srcDoc"),
    Input("target_input_y", "value"),
    Input("region_input", "value"),
    Input("year_input", "value"),
)
def chart_top_countries(target, region, year):
    """
    Create bar chart for top 10 countries based on the statistic of interest

    Parameters
    --------
    target: string
        Selection from statistic of interest filter
    region: string
        Selection from the region button filter
    year: int
        Selection from the year dropdown filter

    Returns
    --------
    bar_chart
        bar chart showing top 10 coutries on the target/ statistic of interest

    Example
    --------
    > chart_top_countries("life_expectany", "Americas", 2000 )
    """
    alt.themes.enable("none")

    # creating dataframe based on year and region
    gm_target = gapminder[gapminder["year"].dt.year == 1950]
    if region != "All":
        gm_target = gm_target[gm_target["region"] == region]

    gm_target.sort_values(by=target, axis=0, ascending=False, inplace=True)

    # Dataframe that holds the top 10 values
    df = gm_target[:10]

    title = (
        "Top 10 countries in the world"
        if region == "All"
        else "Top 10 countries in the Americas"
        if region == "Americas"
        else "Top 10 countries in " + region
    )
    # PLot the bar_chart
    bar_chart = (
        alt.Chart(
            df,
            title=title,
            padding={"left": 20, "right": 0},
        )
        .mark_bar(size=22)
        .encode(
            y=alt.Y("country", sort="-x", title=""),
            x=alt.X(
                target, title=target.lower().replace("_", " ").capitalize()
            ),
            tooltip=target,
        )
        .configure_axis(labelFontSize=14, titleFontSize=14)
        .properties(width=200, height=250)
        .configure_view(strokeWidth=0)
        .configure_title(fontSize=20, anchor="start", color="#5C0029")
    )

    return bar_chart.to_html()


# Set up callbacks/backend
@app.callback(
    Output("bubble_plot", "srcDoc"),
    Input("year_input", "value"),
    Input("region_input", "value"),
    Input("target_input_y", "value"),
    Input("target_input_x", "value"),
)
def plot_lifeexp_gdp(year, region, target_y, target_x):
    """
    Create map plot for statsitic of interested based on selected filters
    Parameters
    --------
    year : int
        Selection from the year dropdown
    region: string
        Selection from the Region filter
    target_y: string
        Selection from target of interest filter for y-axis of the plot
    target_x: string
        Selection from target of interest filter for x-axis of the plot
    Returns
    --------
    scatter_pop_lifeexp
        scatter plot chart showing relation between targets of interest
    Example
    --------
    > plot_lifeexp_gdp("gdp", "life_expectancy")
    """

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

    y_title = list(
        filter(lambda dic: dic["value"] == target_y, opt_dropdown_targets)
    )[0]["label"]

    x_title = list(
        filter(lambda dic: dic["value"] == target_x, opt_dropdown_targets)
    )[0]["label"]

    scatter_pop_lifeexp = (
        alt.Chart(
            gap_filtered,
            title=f"{y_title} vs. {x_title}",
            padding={"left": 20, "right": 0, "top": 0},
        )
        .mark_circle()
        .encode(
            x=alt.X(target_x, title=x_title),
            y=alt.Y(target_y, title=y_title),
            color=alt.Color("region", title="Region"),
            size=alt.Size("population", title="Population"),
            tooltip = ['name', target_x, target_y]
        )
        .configure_axis(labelFontSize=14, titleFontSize=14)
        .configure_legend(titleFontSize=14, titleColor="#5C0029")
        .configure_title(fontSize=20, anchor="start", color="#5C0029")
        .properties(width=250, height=150)
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
    Create map plot for target of interest based on the selected filters
    Parameters
    --------
    target: string
        Selection from target of interest filter
    region: string
        Selection from the region filter
    Returns
    --------
    map_chart
        map chart showing target of interest for specific region
    Example
    --------
    > plot_map("Asia", "life_expectany")
    """
    alt.data_transformers.disable_max_rows()

    alt.themes.enable("none")

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

    target_title = list(
        filter(lambda dic: dic["value"] == target, opt_dropdown_targets)
    )[0]["label"]

    region_title = "the Americas" if region == "Americas" else region

    title = (
        "Global " + target_title
        if region == "All"
        else target_title + " in " + region_title
    )

    map_chart = (
        alt.Chart(
            world_map,
            title=f"{title}",
        )
        .mark_geoshape(stroke="black")
        .transform_lookup(
            lookup="id",
            from_=alt.LookupData(data, key="id", fields=["name", target]),
        )
        .encode(
            tooltip=["name:O", target + ":Q"],
            color=alt.Color(
                target + ":Q",
                title=f"{target_title}",
                legend=alt.Legend(
                    orient="none",
                    legendX=440,
                    legendY=20,
                    direction="horizontal",
                    titleAnchor="end",
                    titleColor="#5C0029",
                ),
            ),
        )
    )

    final_map = (
        (background + map_chart)
        .configure_view(strokeWidth=0)
        .properties(width=600, height=450, padding={"left": 20, "right": 0})
        .configure_title(fontSize=20, anchor="start", color="#5C0029")
        .configure_legend(titleFontSize=14)
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
def plot_line(target, region, country, year):
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

    # creating dataframe that include country, region and whole world of target study
    # world
    df = gapminder.groupby(["year"]).mean().reset_index()[["year", target]]
    df["label"] = "World"

    # region
    if region != "All":
        gm_region = gapminder[gapminder["region"] == region]
        df_region = (
            gm_region.groupby(["year"]).mean().reset_index()[["year", target]]
        )
        df_region["label"] = region
        df = pd.concat([df, df_region])

    # country
    if len(country) != 0:
        gm_country = gapminder[gapminder["country"] == country]
        df_country = (
            gm_country.groupby(["year"]).mean().reset_index()[["year", target]]
        )
        df_country["label"] = country
        df = pd.concat([df, df_country])

    # Using year
    df = df.query("year <= @year")

    # Dataframe that holds the last value
    text_order = df.loc[df["year"] == df["year"].max()].sort_values(
        target, ascending=False
    )

    # PLot
    y_title = list(
        filter(lambda dic: dic["value"] == target, opt_dropdown_targets)
    )[0]["label"]

    line_chart = (
        alt.Chart(df, title=f"{y_title} from 1950 to {year}")
        .mark_line()
        .encode(
            alt.X("year", title="Date"),
            alt.Y(target, title=y_title),
            color=alt.Color("label", legend=None),
            tooltip=["label", target],
        )
        .properties(width=250, height=150)
    )

    text = (
        alt.Chart(text_order)
        .mark_text(dx=30)
        .encode(
            x="year",
            y=target,
            text="label",
            color="label",
            tooltip=["label", target],
        )
    )

    return (
        (line_chart + text)
        .configure(padding={"left": 50, "right": 0})
        .configure_view(strokeWidth=0)
        .configure_axis(
            labelFontSize=14,
            titleFontSize=14,
        )
        .configure_legend(titleFontSize=14)
        .configure_title(fontSize=20, anchor="start", color="#5C0029")
        .to_html()
    )


if __name__ == "__main__":
    app.run_server(debug=True)
