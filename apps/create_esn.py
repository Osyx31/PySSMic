import base64
import datetime
import io
import json
import xml.etree.ElementTree as ET
import pandas as pd

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from backend.neighbourhood import Neighbourhood
from backend.house import House
from backend.device import Device
from backend.user import User

from app import app

# Returns a list of divs.

# TODO: modal for adding house. modal with input field to set houseID


def create_neighborhood_output(nei):
    houses = []
    for house in nei.houses:
        houses.append(displayHouse(house))
    return houses

# Takes in a house object. see backend.house


def displayHouse(house):
    numOfUsers = 0
    numOfDevices = 0
    for user in house.users:
        numOfUsers += 1
        for device in user.devices:
            numOfDevices += 1

    return html.Div(["House",
                     html.Span(str(house.id)),
                     html.Button("Config house"),
                     html.Br(),
                     html.Span("Number of users: " + str(numOfUsers)),
                     html.Br(),
                     html.Span("Number of devices: " + str(numOfDevices)),
                     html.Br()
                     ])


def addHouseToNeighbourhood(neighbourhood):
    lastId = int(neighbourhood.houses[-1].id)
    house = House(lastId + 1)
    neighbourhood.houses.append(house)
    return neighbourhood


def newHouseModal():
    return html.Div(
        html.Div(
            [
                html.Div(
                    [
                        # header
                        html.Div(
                            [
                                html.Span(
                                    "New House - ID X",
                                    style={
                                        "color": "#506784",
                                        "fontWeight": "bold",
                                        "fontSize": "20",
                                    },
                                ),
                                html.Span(
                                    "×",
                                    id="leads_modal_close",
                                    n_clicks=0,
                                    style={
                                        "float": "right",
                                        "cursor": "pointer",
                                        "marginTop": "0",
                                        "marginBottom": "17",
                                    },
                                ),
                            ],
                            className="popup",
                            style={"borderBottom": "1px solid #C8D4E3"},
                        ),
                        # form
                        html.Div(
                            [
                                html.P(
                                    [
                                        "Here you can add settins for the popup. See link commented in code",
                                        # Ex: https://github.com/plotly/dash-salesforce-crm/blob/master/apps/leads.py

                                    ],
                                    style={
                                        "float": "left",
                                        "marginTop": "4",
                                        "marginBottom": "2",
                                    },
                                    className="row",
                                ),
                            ],
                            className="row",
                            style={"padding": "2% 8%"},
                        ),
                        # create house button
                        html.Span(
                            "Submit",
                            id="submit_new_lead",
                            n_clicks=0,
                            className="button button--primary add"
                        ),
                    ],
                    className="modal-content",
                    style={"textAlign": "center"},
                )
            ],
            className="modal",
        ),
        id="house_modal",
        style={"display": "none"},
    )


layout = html.Div([
    # hidden div to save data in
    html.Div(id="hidden-div", style={'display': 'none'}),
    html.H4("Create a new neighbourhood"),

    dcc.Upload(
        id="upload-data",
        children=html.Div([
            'Add neighbourhood XML file by Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        }
    ),
    html.Button("Add house", id='btnAddHouse'),
    html.Br(),
    html.Div(id='output'),
    newHouseModal()
])

# takes in a xmlfile and returns a XML Elementree of the neighborhood.


def parse_contents(contents):
    if contents is not None:
        content_type, content_string = contents.split(',')
        if 'xml' in content_type:
            decoded = base64.b64decode(content_string)
            root = ET.fromstring(decoded)
            return root


def create_neighborhood_object(treeroot):
    nabolag = Neighbourhood(treeroot.get("id"))
    for house in treeroot:
        h = House(house.get("id"))
        for user in house:
            u = User(user.get("id"))
            for device in user:
                d = Device(int(device.find("id").text), device.find("name").text, int(
                    device.find("template").text), device.find("type").text)
                u.devices.append(d)
            h.users.append(u)
        nabolag.houses.append(h)
    return nabolag


def eltreeToDataframe(treeRoot):
    df = pd.DataFrame(columns=[
        "houseId", "deviceId", "UserId", "DeviceName", "DevTemp", "DevType"])
    for house in treeRoot:
        for user in house:
            for device in user:
                df = df.append({"houseId": (house.get("id")), "deviceId": (device.find("id").text), "UserId": (user.get("id")), "DeviceName": (device.find("name").text), "DevTemp": (device.find("template").text), "DevType": (device.find("type").text)},
                               ignore_index=True)
    # df.set_index("deviceId", inplace=True)
    return df


def addDevice(data, houseId, deviceId, userId, deviceName, devTemp, devType):
    df = data
    df2 = pd.DataFrame([[houseId, userId, deviceName, devTemp, devType]], index=[
        deviceId], columns=["houseId", "UserId", "DeviceName", "DevTemp", "DevType"])
    return pd.concat([df, df2])


"""
@app.callback(Output('output', 'children'), [Input('neighbourhood-div', 'children')])
def show_house():
   """


@app.callback(Output('output', 'children'), [Input('upload-data', 'contents')])
def create_house(contents):
    root = parse_contents(contents)
    nei = create_neighborhood_object(root)
    nabolag = create_neighborhood_output(nei)
    return html.Div(children=nabolag)


# hide/show popup


@app.callback(Output("house_modal", "style"), [Input("btnAddHouse", "n_clicks")])
def display_leads_modal_callback(n):
    if n > 0:
        return {"display": "block"}
    return {"display": "none"}

# reset to 0 add button n_clicks property


@app.callback(
    Output("btnAddHouse", "n_clicks"),
    [Input("leads_modal_close", "n_clicks"),
     Input("submit_new_lead", "n_clicks")],
)
def close_modal_callback(n, n2):
    return 0
