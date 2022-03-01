from dash import Dash, dcc, html, Input, Output
import pandas as pd
import altair as alt

# Read the data
gm = pd.read_csv('data/raw/gapminder_2018.csv', parse_dates=['year'])


# Set-up the app and user interface
gapminder_app = Dash(__name__)
server = gapminder_app.server

gapminder_app.layout = html.Div([
    html.Iframe(
        id='scatter',
        style={'border-width': '0', 'width': '100%', 'height': '400px'}),
    dcc.Dropdown(
        id='xcol-widget', value='children_per_woman',
        options=[{'label': col, 'value': col} for col in gm_2018.columns])])

# Setup callbacks
@gapminder_app.callback(
    Output('scatter', 'srcDoc'),
    Input('xcol-widget', 'value'))

def plot_chart(xcol):
    chart = alt.Chart(gm_2018).mark_point(filled=True).encode(
        x=xcol,
        y='life_expectancy',
        tooltip='country',
        color='region',
        size='population').interactive()
    return chart.to_html()

if __name__ == '__main__':
    gapminder_app.run_server(debug=True)