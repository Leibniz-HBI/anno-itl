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
        html.H3("Annotation in the Loop", className="text-center"),
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

text_unit_view = dbc.Col(
    id="text-unit-view", children=[
        dbc.Row(
            dbc.Col(
                id='text-unit-header',
                children=[
                    html.H5('Text unit view', className="text-center", id='text-unit-header-text'),
                    dbc.Button("fetch new data", className="float-start"),
                ]
            ),
            className="sticky-top bg-white"
        ),
        dbc.Row(
            dbc.Col(
                [html.Div('load a project and work through those text snippets!'),
                html.Div(
                    hidden=True,
                    id='dirty-bit',
                    **{
                        'data-changed': 0,
                        'data-labelchanged': 0
                    }
                )],
                id='text-unit-data',
            )
        )
    ],
)


algo_result_view = dbc.Col(
    id='algo-view',children=[
        dbc.Row(
            dbc.Col(
                id='algo-header',
                children=[
                    html.H5('Similarity Search Results', className="text-center")
                ]
            ),
            className="sticky-top bg-white"
        ),
        dbc.Row(
            dbc.Col(
                html.Div('load a project and find those similarities!'),
                id='algo-results',

            )
        )
    ],
)


label_list_header = html.H6("Labels", className="border-2 text-center text-white bg-info mt-0 mb-2")


label_add_components = html.Div(
    [
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
    hidden=True,
    id='label-buttons'
)

label_menu = dbc.Col(
    children=[
        dbc.Row(
            id="label-header",
            children=label_add_components,
            className="border-bottom border-2 border-dark g-0 mb-0",
        ),
        dbc.Row(
            dbc.Col(id='label-list', children=[
                "Load a project and see its labels here"
            ])
        )],
)


sidebar = dbc.Col(
    dbc.Accordion([
        dbc.AccordionItem(
            [
                dbc.Row(label_menu),

            ],
            title='Labels',
            id='accordion-label-view'
        )],
        id='sidebar-accordion',
        start_collapsed=True
    ),
    id='sidebar',
    width=2,
    className="border-end border-3 border-danger"
)


layout = dbc.Container([
    html.Div(hidden=True, id='modal-container'),
    header,
    dbc.Row([
        sidebar,
        dbc.Col([
            dbc.Row(
                text_unit_view,
                style={'height': '50%'},
                class_name="overflow-auto border-3 border-danger border-bottom"
            ),
            dbc.Row(
                algo_result_view,
                style={'height': '50%'},
                class_name="overflow-auto"
            )],
            width=10,
            style={'height': '100%'},
            className="border-3 border-danger"
        )],
        style={'height': '90%'},
    )],
    fluid=True, style={"height": "100vh"}

)
