from dash import Dash, html, dcc, Input, Output  # pip install dash
import plotly.express as px
import dash_ag_grid as dag                       # pip install dash-ag-grid
import dash_bootstrap_components as dbc          # pip install dash-bootstrap-components
import pandas as pd                              # pip install pandas
from dash_dangerously_set_inner_html import DangerouslySetInnerHTML

import matplotlib                                # pip install matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import psycopg


class DataSets:

    def __init__(self):
        self.field_notes = pd.read_csv("./field_notes.csv")
        with psycopg.connect(
                "host=localhost port=5432 dbname=postgres user=postgres password=postgres"
            ) as conn:
            self.sql_data = pd.read_sql("""
                select
                    upper(array_to_string(regexp_matches(n.device_id, '(.*)-.*-(.*)'), '-')) as device_id,
                    m.value as value,
                    mt.unit as unit,
                    mt.type_name as measurement_type,
                    m.timestamp as timestamp
                from
                    measurements as m
                join
                    nodes as n
                on
                    n.dev_eui = m.dev_eui
                join
                    measurement_type as mt
                on
                    mt.type_id = m.type_id
                order by "timestamp" asc
            """, conn)

        self.field_notes.set_index('device_id')
        self.sql_data.set_index('device_id')
        self.sql_data_field_notes = self.sql_data.merge(self.field_notes, on='device_id')
        self.current_filtered_dataset = None

data = DataSets()

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = dbc.Container([
    html.H1("Interactive Matplotlib with Dash", className='mb-2', style={'textAlign':'center'}),
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id='category',
                clearable=False,
                options=data.field_notes['device_id'])
        ], width=4),
        dbc.Col([
            dcc.Dropdown(id="my-multi-dynamic-dropdown"),
        ]),
    ]),
    dbc.Row([
        dbc.Col([
            html.Img(id='bar-graph-matplotlib')
        ], width=12)
    ]),
    html.Div(
        [html.Div(id='transect_output')],
    ),

])

# Create interactivity between dropdown component and graph
@app.callback(
    # Output(component_id='bar-graph-matplotlib', component_property='src'),
    Output("my-multi-dynamic-dropdown", "options"),
    Output("transect_output", "children"),
    Input('category', 'value'),
)
def plot_data(selected_yaxis):

    # Build the matplotlib figure
    fig = plt.figure(figsize=(14, 5))
    filtered_dataset = data.sql_data_field_notes.loc[data.sql_data_field_notes['device_id'] == selected_yaxis]
    data.current_filtered_dataset = filtered_dataset
    transect_notes = data.field_notes.loc[data.field_notes['device_id'] == selected_yaxis]

    # return fig_bar_matplotlib, filtered_dataset['unit'].unique()
    return filtered_dataset['unit'].unique(), DangerouslySetInnerHTML(transect_notes.to_html())


# Create interactivity between dropdown component and graph
@app.callback(
    Output(component_id='bar-graph-matplotlib', component_property='src'),
    Input('my-multi-dynamic-dropdown', 'value'),
)
def plot_data_filtered(selected_yaxis):

    # Build the matplotlib figure
    fig = plt.figure(figsize=(14, 5))
    filtered_dataset = data.current_filtered_dataset.loc[data.current_filtered_dataset['unit'] == selected_yaxis]

    plt.plot(filtered_dataset['timestamp'], filtered_dataset['value'])
    plt.ylabel(selected_yaxis)
    plt.xticks(rotation=30)

    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")
    # Embed the result in the html output.
    fig_data = base64.b64encode(buf.getbuffer()).decode("ascii")
    fig_bar_matplotlib = f'data:image/png;base64,{fig_data}'

    # Build the Plotly figure

    my_cellStyle = {
        "styleConditions": [
            {
                "condition": f"params.colDef.field == '{selected_yaxis}'",
                "style": {"backgroundColor": "#d3d3d3"},
            },
            {   "condition": f"params.colDef.field != '{selected_yaxis}'",
                "style": {"color": "black"}
            },
        ]
    }

    return fig_bar_matplotlib


if __name__ == '__main__':
    app.run_server(debug=False, port=8002)