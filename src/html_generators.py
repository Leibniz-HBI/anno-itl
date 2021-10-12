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


dataset_name_input = dbc.FormGroup([
    dbc.Input(placeholder="Dataset Name", type="text", id='dataset-name-input'),
    dbc.FormText("Please only _, A-Z,a-z and numbers; between 4 and 30 characters"),
    dbc.FormFeedback(
    "name is valid and not taken", valid=True
    ),
    dbc.FormFeedback(
    "This name is not okay (never displayed, I think)",
    id = 'dataset-name-invalid-message',
    valid=False,
    )
])


dataset_upload = dbc.FormGroup([
   dcc.Upload(
    id='upload-dataset',
    children=html.Div([
        'Drag and Drop or ',
        html.A('Select File')
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
),
dbc.FormText('select an csv, ctv or xls file, please!')
])

dataset_description_input = dbc.FormGroup([
    dbc.Textarea(placeholder='Dataset description', id='dataset-description-input'),
    dbc.FormText("short description of the dataset, min 10, max 500 characters, no special chars please or I will personally come to your door"),
    dbc.FormFeedback(
    "Description is valid, at least formally.", valid=True
    ),
    dbc.FormFeedback(
    "This name is not okay (never displayed, I think)",
    id = 'dataset-description-invalid-message',
    valid=False,
    )
])

dataset_button = dbc.Button("Create!", color="warning", id='add-dataset')

create_dataset_form = dbc.Form([dataset_name_input,
                               dataset_upload,
                               dataset_description_input,
                               dataset_button
                              ])


def open_project_modal():
    modal = dbc.Modal([
    dbc.ModalHeader("Open or create a new project"),
    dbc.ModalBody(
        dbc.Tabs(
        [
        dbc.Tab(
            dbc.Card(
                dbc.CardBody([
                    html.H4("Open", className="card-title"),
                    html.P("This is tab 1!", className="card-text"),
                    dbc.Button("Click here", color="success"),
                ]),
            ),
            label= "Open Project"
        ),
        dbc.Tab(
            dbc.Card(
                dbc.CardBody([
                    html.H4("Create new Dataset", className="card-title"),
                    create_dataset_form
                    ]),
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

