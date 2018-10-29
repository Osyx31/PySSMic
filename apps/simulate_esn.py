import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, Event, State
import dash_table_experiments as dt
import plotly.graph_objs as go
import json
import pandas as pd
from app import app

"""-------------------------ENERGY USE-------------------------"""


def get_energy_df():
    return pd.DataFrame({'c1': [384, 827], 'c2': [848, 874]})


def energy_use(df):
    df_sum = df.sum(axis=1)
    n = 100/(df_sum[0]+df_sum[1])
    return (
        dcc.Graph(
            id="energy-use-graph",
            figure=go.Figure(
                data=[
                    go.Pie(
                        values=[df_sum[0]*n, df_sum[1]*n],
                        labels=["Local", "Not local"]
                    )
                ]
            )
        )
    )


""""-------------------------CONTRACT OVERVIEW-------------------------"""


def contract_overview():
    return (
        dt.DataTable(
            rows=[{}],
            columns=[
                "id", "time_of_agreement", "job_id", "producer_id"],
            row_selectable=True,
            filterable=True,
            sortable=True,
            selected_row_indices=[],
            id="contract-table"
        )
    )


"""-------------------------AVAILABLE VS USED ENERGY-------------------------"""


def get_consumption():
    return


def energy_consumption():
    return (
        dcc.Graph(
            id="energy-consumption-graph",
            figure=go.Figure(
                data=[
                    # TODO: Update to input values from simulator in 'get_consumption()'
                    go.Scatter(
                        x=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23], y=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1],
                        name="Energy used"
                    ),
                    go.Scatter(
                        x=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23], y=[6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6],
                        name="Energy available"
                    )
                ],
                layout=go.Layout(
                    xaxis={
                        'title': 'Time'
                    },
                    yaxis={
                        'title': 'Energy'
                    }
                )
            )
        )
    )


"""-------------------------LAYOUT-------------------------"""
layout = html.Div([
    dcc.Tabs(id="tabs", children=[
            dcc.Tab(label='All households', children=[
                html.Div(
                    html.H2("Energy use")
                ),
                html.Div([
                    energy_use(get_energy_df())
                ], className="pie-chart"),

                html.Div(
                    html.H2("Contracts")
                ),
                html.Div([
                    contract_overview()
                ], className="contract-table"),

                html.Div(
                    html.H2("Available vs Used energy")
                ),
                html.Div([
                    energy_consumption()
                ], className="consumption-graph"),
                html.Button("Start simulation", id="btnSimulationStart")
            ]),
            dcc.Tab(label='One household', children=[
                #TODO
            ])
    ])
])


@app.callback(Output("contract-table", "rows"),
              [Input("btnSimulationStart", "n_clicks"),
               Input('datatableDiv', 'children')])
def update_table(n, children):
    if n and n > 0:
        return json.loads(children)
