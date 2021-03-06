"""The main layout of the app. Bootstrap grid style layout, everything's on rows
and grids. Paddings and margins are set with class name attributes e.g. pt-1 for
1 sized padding at the top of an element. For more info, check out
(bootstrap)[https://getbootstrap.com/]

The Layout consists mainly of two Rows (in a container).
The first row is the header and the second row is the content.

The header has two columns, one for the buttons/menu and one for the title
The content has three columns:
1. the labels
2. the text data. (consisting of two rows, one for text data, one for algorithm output)
3. the third that, uhm, I like. (yes, yes, it will go if I don't find use.)
"""

from dash import dash_table
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc


header = dbc.Row([
    dbc.Col([
        dbc.Button('Open or create project', id='btn-new-data'),
        dbc.Button("Save!", color='danger', id='btn-save-data', disabled=True),
        html.Div(hidden=True, id='clean-bit', **{'data-saved': 0}),
        dcc.Store(id='current_dataset'),
        dcc.Store(id='new_data')
    ],
        align="end",
        width=4,
        id='header-button-col',
        # class_name="pb-1"
    ),
    dbc.Col(
        html.H3("Test Layout using the Grid", style={'textAlign': 'center'}),
        align='center',
        width=4,
        id='header-title-col',
    ),
],
    style={'height': '10%'},
    className="border-bottom border-3 border-danger",
    justify="start",
    id='app-header',
)

text_unit_box = dbc.Col(
    id="arg-list-box", children=[
        html.Div('Argument Input', id="arg-list-header"),
        dash_table.DataTable(
            id='arg-table',
            filter_action="native",
            columns=[
                {'name': 'Argument', 'id': 'text unit'},
                {
                    'name': 'Label', 'id': 'label',
                    'editable': True, 'presentation': 'dropdown'
                }
            ],
            data=[],
            style_header={
                'text_Align': 'center',
            },
            style_data={
                'whiteSpace': 'normal',
                'height': 'auto',
                'page_size': '50',
            },
            style_data_conditional=[
                {
                    'if': {'column_id': 'text unit'},
                    'textOverflow': 'ellipsis',
                    'maxWidth': 0,
                    'width': '90%',
                    'textAlign': 'left'
                    # 'cursor': 'pointer'
                }
            ]
        ),
        html.Div(hidden=True, id='dirty-bit', **{'data-changed': 0})
    ],
)


algo_result_box = dbc.Col(
    id='algo-box', children=[
        html.Div('Similar Arguments', id="algo-box-header"),
        dash_table.DataTable(
            id='algo-table',
            columns=[
                {'name': 'Argument', 'id': 'text unit'},
                {
                    'name': 'Label', 'id': 'label',
                    'editable': True, 'presentation': 'dropdown'
                }
            ],
            data=[],
            style_header={
                'text_Align': 'center',
            },
            style_data={
                'whiteSpace': 'normal',
                'height': 'auto',
                'page_size': '50',
            },
            style_data_conditional=[
                {
                    'if': {'column_id': 'text unit'},
                    'textOverflow': 'ellipsis',
                    'maxWidth': 0,
                    'width': '90%',
                    'textAlign': 'left'
                }
            ]
        )]
)

label_list_header = html.H6("Labels", className="border-2 text-center text-white bg-info mt-0 mb-2")

label_column = dbc.Col(
    children=[
        dbc.Row(
            id="label-header",
            children=[
                dbc.Col(
                    dbc.Input(id='lbl-input', placeholder='Add Label..', type='text'),
                    width=9
                ),
                dbc.Col(
                    dbc.Button(
                        id='submit-lbl-button',
                        color='primary', children='Add', style={'width': '100%'}),
                    width=3
                )
            ],
            className="border-bottom border-2 border-dark g-0 mb-0",
        ),
        dbc.Row(
            dbc.Col(id='label-list', children=[label_list_header])
        )],
    width=2,
    className="border-end border-3 border-danger"
)

layout = dbc.Container([
    html.Div(hidden=True, id='modal-container'),
    header,
    dbc.Row([
        label_column,
        dbc.Col([
            dbc.Row(
                text_unit_box,
                style={'height': '50%'},
                class_name="overflow-auto"
            ),
            dbc.Row(
                algo_result_box,
                style={'height': '50%'},
                class_name="overflow-auto"
            )],
            width=8,
            style={'height': '100%'},
            className="border-end border-3 border-danger"
        ),
        dbc.Col([dbc.Button("row 1 col 3", style={"width": "100%"})], width=2)],
        style={'height': '90%'},

    )],
    fluid=True, style={"height": "100vh"}, class_name="background-main"
)
