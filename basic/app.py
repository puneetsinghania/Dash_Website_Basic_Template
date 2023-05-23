# -*- coding: utf-8 -*-
import dash
from dash import dcc
from dash import html
from dash import dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go 

import os
import urllib.parse
from flask import Flask, send_from_directory, request

import pandas as pd
import requests
import uuid
import werkzeug

import numpy as np
from tqdm import tqdm
import urllib
import json


from collections import defaultdict
import uuid

from flask_caching import Cache

import networkx as nx
from plotly.graph_objs import Scatter, Figure


# Functions for creating and visualizing a tree from JSON
def add_tree_data(G, parent_node, json_dict):
    """
    Recursive function to add nodes to the tree
    """
    for k, v in json_dict.items():
        if isinstance(v, dict):
            G.add_edge(parent_node, v["name"])
            add_tree_data(G, v["name"], v)
        elif isinstance(v, list):
            for child in v:
                G.add_edge(parent_node, child["name"])
                add_tree_data(G, child["name"], child)

def create_tree(json_dict):
    """
    Create a networkx tree from the json dictionary
    """
    G = nx.DiGraph()
    root = json_dict["name"]
    add_tree_data(G, root, json_dict)
    return G


def draw_graph(G):
    """
    Draw the graph using plotly
    """
    pos = nx.spring_layout(G)
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)

    edge_trace = Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')

    node_x = [pos[node][0] for node in G.nodes()]
    node_y = [pos[node][1] for node in G.nodes()]

    node_trace = Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            colorscale='YlGnBu',
            reversescale=True,
            color=[],
            size=10,
            colorbar=dict(
                thickness=15,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            ),
            line_width=2))

    node_text = [node for node in G.nodes()]
    node_trace.text = node_text

    fig = Figure(data=[edge_trace, node_trace],
                 layout=go.Layout(
                    title=dict(text='Tree structure'),
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20, l=5, r=5, t=40),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )
    return fig

server = Flask(__name__)
app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = 'Wang Lab - Dashboard Template'

cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'temp/flask-cache',
    'CACHE_DEFAULT_TIMEOUT': 0,
    'CACHE_THRESHOLD': 10000
})

server = app.server


NAVBAR = dbc.Navbar(
    children=[
        dbc.NavbarBrand(
            html.Img(src="https://gnps-cytoscape.ucsd.edu/static/img/GNPS_logo.png", width="120px"),
            href="https://mingxunwang.com"
        ),
        dbc.Nav(
            [
                dbc.NavItem(dbc.NavLink("Wang Bioinformatics Lab - Template Dashboard - Version 0.1", href="#")),
            ],
        navbar=True)
    ],
    color="light",
    dark=False,
    sticky="top",
)

DATASELECTION_CARD = [
    dbc.CardHeader(html.H5("Data Selection")),
    dbc.CardBody(
        [   
            html.H5(children='Data Selection'),
            dbc.InputGroup(
                [
                    dbc.InputGroupText("JSON URL"),
                    dbc.Input(id='json_url', placeholder="Enter URL for JSON file", value=""),
                ],
                className="mb-3",
            ),
            dbc.Button("Copy Link", color="info", id="copy_link_button", n_clicks=0),
            html.Div(
                [
                    dcc.Link(id="query_link", href="#", target="_blank"),
                ],
                style={
                        "display" :"none"
                }
            )
        ]
    )
]

LEFT_DASHBOARD = [
    html.Div(
        [
            html.Div(DATASELECTION_CARD),
        ]
    )
]

MIDDLE_DASHBOARD = [
    dbc.CardHeader(html.H5("Data Exploration")),
    dbc.CardBody(
        [
            dcc.Loading(
                id="output",
                children=[html.Div([html.Div(id="loading-output-23")])],
                type="default",
            ),
        ]
    )
]

CONTRIBUTORS_DASHBOARD = [
    dbc.CardHeader(html.H5("Contributors")),
    dbc.CardBody(
        [
            "Mingxun Wang PhD - UC Riverside",
            html.Br(),
            html.Br(),
            html.H5("Citation"),
            html.A('Mingxun Wang, Jeremy J. Carver, Vanessa V. Phelan, Laura M. Sanchez, Neha Garg, Yao Peng, Don Duy Nguyen et al. "Sharing and community curation of mass spectrometry data with Global Natural Products Social Molecular Networking." Nature biotechnology 34, no. 8 (2016): 828. PMID: 27504778', 
                    href="https://www.nature.com/articles/nbt.3597"),
            html.Br(),
            html.Br(),
            html.A('Checkout our other work!', 
                href="https://www.cs.ucr.edu/~mingxunw/")
        ]
    )
]

EXAMPLES_DASHBOARD = [
    dbc.CardHeader(html.H5("Examples")),
    dbc.CardBody(
        [
            html.A('Basic', 
                    href=""),
        ]
    )
]

BODY = dbc.Container(
    [
        dcc.Location(id='url', refresh=False),
        dbc.Row([
            dbc.Col(
                dbc.Card(LEFT_DASHBOARD),
                className="w-50"
            ),
            dbc.Col(
                [
                    dbc.Card(MIDDLE_DASHBOARD),
                    html.Br(),
                    dbc.Card(CONTRIBUTORS_DASHBOARD),
                    html.Br(),
                    dbc.Card(EXAMPLES_DASHBOARD)
                ],
                className="w-50"
            ),
        ], style={"marginTop": 30}),
    ],
    fluid=True,
    className="",
)
app.layout = html.Div(children=[NAVBAR, BODY])

def _get_url_param(param_dict, key, default):
    return param_dict.get(key, [default])[0]

@app.callback([
                Output('query_link', 'href'),
              ],
                [
                    Input('json_url', 'value'),
                ])
def draw_url(json_url):
    params = {}
    params["json_url"] = json_url

    url_params = urllib.parse.urlencode(params)

    return [request.host_url + "/?" + url_params]

@app.callback(
    Output('output', 'children'),
    [Input('json_url', 'value')])
def draw_output(json_url):
    if json_url:
        response = requests.get(json_url)
        if response.status_code == 200:
            try:
                json_data = response.json()
                if "children" in json_data:
                    # JSON structure with "children" field
                    tree = create_tree(json_data)
                    graph = draw_graph(tree)  # Convert the tree to a plotly figure
                    return [html.Div(children=[dcc.Graph(figure=graph)])]
                elif "nodes" in json_data:
                    # JSON structure with "nodes" field
                    G = nx.DiGraph()
                    for node in json_data["nodes"]:
                        parent = node["parent"]
                        if parent == "":
                            parent = "Root"
                        G.add_edge(parent, node["name"])
                    graph = draw_graph(G)  # Convert the graph to a plotly figure
                    return [html.Div(children=[dcc.Graph(figure=graph)])]
                else:
                    return [html.Div("Error: Invalid JSON structure")]
            except json.decoder.JSONDecodeError as e:
                return [html.Div(f'Error: Failed to decode JSON. Reason: {str(e)}')]
        else:
            return [html.Div(f'Error: Request failed with status code {response.status_code}')]
    else:
        return [html.Div(children=[f'Please enter a JSON URL'])]
        
app.clientside_callback(
    """
    function(n_clicks, button_id, text_to_copy) {
        original_text = "Copy Link"
        if (n_clicks > 0) {
            const el = document.createElement('textarea');
            el.value = text_to_copy;
            document.body.appendChild(el);
            el.select();
            document.execCommand('copy');
            document.body.removeChild(el);
            setTimeout(function(id_to_update, text_to_update){ 
                return function(){
                    document.getElementById(id_to_update).textContent = text_to_update
                }}(button_id, original_text), 1000);
            document.getElementById(button_id).textContent = "Copied!"
            return 'Copied!';
        } else {
            return original_text;
        }
    }
    """,
    Output('copy_link_button', 'children'),
    [
        Input('copy_link_button', 'n_clicks'),
        Input('copy_link_button', 'id'),
    ],
    [
        State('query_link', 'href'),
    ]
)

# API
@server.route("/api")
def api():
    return "Up"    

if __name__ == "__main__":
    app.run_server(debug=True, port=5000, host="0.0.0.0")
