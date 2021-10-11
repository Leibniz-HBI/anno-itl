"""Here are all the generated html pieces that are needed.
"""

from dash import dcc
import dash.html as html
from dash.html.Tr import Tr
from dash.dependencies import Input, Output, State, MATCH, ALL
import plotly.express as px
import dash_bootstrap_components as dbc


def create_table_row(input_tuple):
    """Create a dash table row from a tuple of inputs
    """
    return html.Tr([html.Td(value) for value in input_tuple])


def create_details_table(sentence_data, header='Details Box View'):
    """Creates a details view for a selected sentence.
    """
    return html.Table(
        className='details-table',
        children=[
            html.Thead(header),
            html.Tbody(
                children=[create_table_row((k, v)) for k, v in sentence_data.items()]
            )
        ]
    )


def open_project_modal():
    modal = dbc.Modal(
    [
    dbc.ModalHeader("Open or create a new project"),
    dbc.ModalBody(
        dbc.Tabs(
        [
        dbc.Tab(
            dbc.Card(
                dbc.CardBody(
                    [
                    html.H4("Open", className="card-title"),
                    html.P("This is tab 1!", className="card-text"),
                    dbc.Button("Click here", color="success"),
                    ]
                ),
            ),
            label= "Open Project"
        ),
        dbc.Tab(
            dbc.Card(
                dbc.CardBody(
                    [
                    html.H4("Create new Dataset", className="card-title"),
                    dbc.FormGroup(
                        [
                            dbc.Input(placeholder="Dataset Name", type="text"),
                            dbc.FormText("Please only _A-Z,a-z and numbers"),
                            dcc.Upload(
                                id='upload-data',
                                children=html.Div([
                                    'Drag and Drop or ',
                                    html.A('Select a csv, ctv or xls file')
                                ]),
                                style={
                                    'width': '50%',
                                    'height': '40px',
                                    'lineHeight': '60px',
                                    'borderWidth': '1px',
                                    'borderStyle': 'dashed',
                                    'borderRadius': '5px',
                                    'textAlign': 'center',
                                    'margin': '5px'
                                },
                            )
                        ]
                    ),
                    dbc.Button("Create!", color="warning", id = 'add-dataset')
                    ]
                ),
            ),
            label= "Create New Project"
        )
        ])
    ),
    dbc.ModalFooter(
        dbc.Button(
            "Close", id="close-upload-diag", n_clicks=0
        )
    )
    ],
    id="open-modal",
    size="xl",
    is_open=True,
    )
    return modal

