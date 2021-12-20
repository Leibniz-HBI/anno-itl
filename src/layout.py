"""Describes the main layout of the app, including the panes and the header.
"""

from dash import dash_table
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc


layout = html.Div([
    html.Div(
        id='app-header',
        children=[
            html.Div('Annotation tool with Human in the Loop', id="app-header-title"),
            html.Div(hidden=True, id='clean-bit', **{'data-saved': 0}),
            html.Div([
                dbc.Button("Open or create project", color='primary', id='btn-new-data'),
                dbc.Button("Save!", color='danger', id='btn-save-data', disabled=True)
            ], id='header-buttons')
        ]
    ),
    html.Div(
        id="arg-list-pane",
        children=[
            dcc.Store(id='current_dataset'),
            dcc.Store(id='new_data'),
            html.Div(id="arg-list-box", children=[
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
            ]
            ),
            html.Div('Argument Details', id="argument-detail-box")
        ]
    ),
    html.Div(
        id="label-pane",
        children=[
            html.Div(id="label-box", children=[
                html.Div(
                    id="label-header",
                    children=[
                        dbc.Input(id='lbl-input', placeholder='Add Label..', type='text'),
                        dbc.Button(
                            id='submit-lbl-button',
                            color='primary', n_clicks=0, children='Add')
                    ]),
                html.Ul(
                    id='label_list',
                    children=[
                    ])
            ]),
            html.Div(id='algo-box', children=[
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
        ]
    )
])
