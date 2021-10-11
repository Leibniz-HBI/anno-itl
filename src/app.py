"""Dash application for annotation of short text usign custom categories and
giving suggestions for similar text units.
"""

import re
import pandas as pd
import dash
from dash import dash_table
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State, MATCH, ALL
from dash.html.Button import Button
import dash_bootstrap_components as dbc
import datasets
import html_generators
import table_sync

app = dash.Dash(external_stylesheets=[dbc.themes.JOURNAL],
                suppress_callback_exceptions = True
                )

dcc.Store(id='uploaded-data')

SIMILARITY_SEARCH_RESULTS = 10



sentences_df, search_index = datasets.dataset_from_csv('sentences')

# get all categories which are set in the csv except 'None' values
categories = [cat for cat in sentences_df['category'].unique() if cat]

app.layout = html.Div([
    html.Div(
        className='app-header',
        id = 'app-header',
        children=[
            html.Div('Annotation tool with Human in the Loop', className="app-header--title"),
            dbc.Button("Open or create project", color='primary', id='btn-new-data'),
        ]
    ),
    html.Div(
        className="arg-list-pane",
        children=[
            html.Div(className="arg-list-box", children=[
                html.Div('Argument Input', className="arg-list-header"),
                dash_table.DataTable(
                    id='arg-table',
                    filter_action="native",
                    columns=[
                        {'name': 'Argument', 'id': 'sentence'},
                        {'name': 'Category', 'id': 'category',  'editable':True, 'presentation': 'dropdown'}
                    ],
                    dropdown= {
                        'category': {
                            'options': [
                                {'label': cat, 'value': cat} for cat in categories
                            ]
                        }
                    },
                    data=sentences_df[['id', 'sentence','category']].to_dict('records'),
                    style_header={
                        'text_Align': 'center',
                    },
                    style_data={
                        'whiteSpace': 'normal',
                        'height': 'auto',
                        'page_size': '50',
                    },
                    style_data_conditional=[
                        {'if': {'column_id': 'sentence'},
                        'textOverflow': 'ellipsis',
                        'maxWidth': 0,
                        'width': '90%',
                        'textAlign': 'left'
                        #'cursor': 'pointer'
                        }
                    ]
                )]
            ),
            html.Div('Argument Details', id="argument-detail-box")
        ]
    ),
    html.Div(
        className="category-pane",
        children=[
            html.Div(className="category-box", children=[
                html.Div(
                    className="category-header",
                    children=[
                        dbc.Input(id='cat-input', placeholder='Add Category..', type='text'),
                        dbc.Button(id='submit-cat-button', color='primary', n_clicks=0, children='Add')
                    ]),
                html.Ul(
                    id='cat_list',
                    children=[
                        html.Div(category, {'type': 'category-item', 'index': index},
                                 className="category-container")
                        for index, category in enumerate(categories)
                    ])
                ]
            ),
            html.Div( id='algo-box', children=[
                html.Div('Similar Arguments', className="algo-box-header"),
                dash_table.DataTable(
                    id='algo-table',
                    columns=[
                        {'name': 'Argument', 'id': 'sentence'},
                        {'name': 'Category', 'id': 'category',  'editable':True, 'presentation': 'dropdown'}
                    ],
                    dropdown= {
                        'category': {
                            'options': [
                                {'label': cat, 'value': cat} for cat in categories
                            ]
                        }
                    },
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
                        {'if': {'column_id': 'sentence'},
                        'textOverflow': 'ellipsis',
                        'maxWidth': 0,
                        'width': '90%',
                        'textAlign': 'left'
                        }
                    ]
                )

            ]
            )
        ]
    )
])


@app.callback(
    Output('cat_list', 'children'),
    Output('arg-table', 'dropdown'),
    Output('algo-table', 'dropdown'),
        Input('submit-cat-button', 'n_clicks'),
        Input("cat-input", "n_submit"),
        Input({'type': 'category-remove-btn', 'index': ALL}, 'n_clicks'),
    State('cat-input', 'value'),
    State('cat_list', 'children'),
    State('arg-table', 'dropdown'),
    State('algo-table', 'dropdown')
)
def add_category(n_clicks, n_submit, remove_click, cat_input, children, arg_dropdown, algo_dropdown):
    """Handle Category input.
    Data from the input box can be submitted with enter and button click. If
    that happens, a new category will be created if it doesn't exist yet.
    If the remove button of a category is presesd, the corresponding list
    element will be deleted.
    """
    if (n_clicks or n_submit) and cat_input:
        trigger_id = dash.callback_context.triggered[0]['prop_id']
        if trigger_id.startswith('submit-cat-button') or trigger_id.startswith('cat-input'):
            already_there = False
            for category in children:
                if cat_input in category['props']['children']:
                    already_there = True
            if not already_there:
                new_cat = html.Li(
                    children=[
                        cat_input,
                        html.Button(
                            'remove',
                            id={'type': 'category-remove-btn', 'index': len(children)})
                    ],
                    id={'type': 'category-item', 'index': len(children)},
                    className="category-container")
                children.append(new_cat)
                arg_dropdown['category']['options'] = arg_dropdown['category']['options'] + [{'label': cat_input, 'value': cat_input}]
                algo_dropdown['category']['options'] = algo_dropdown['category']['options'] + [{'label': cat_input, 'value': cat_input}]
        else:
            button_id = int(re.findall('\d+', trigger_id)[0])
            for child in children:
                if child['props']['children'][1]['props']['id']['index'] == button_id:
                    print(child)
                    children.remove(child)
                    try:
                        arg_dropdown['category']['options'].remove(
                            {'label': child['props']['children'][0], 'value': child['props']['children'][0]
                            })
                    except ValueError:
                        print(f'no option {cat_input} in dropdown')
                    try:
                        algo_dropdown['category']['options'].remove(
                            {'label': child['props']['children'][0], 'value': child['props']['children'][0]
                            })
                    except ValueError:
                        print(f'no option {cat_input} in dropdown')

    return children, arg_dropdown, algo_dropdown


@app.callback(
    Output('app-header', 'children'),
        Input('btn-new-data', 'n_clicks'),
    State('app-header', 'children')
)
def load_data_diag(open_clicks, children):
    if not dash.callback_context.triggered[0]['value']:
        raise dash.exceptions.PreventUpdate
    children.append(html_generators.open_project_modal())
    return children


@app.callback(
    Output('upload-dialog', 'is_open'),
    Output("dialog-header", 'children'),
        Input('upload-data', 'contents'),
        Input('close-upload-diag', 'n_clicks'),
    State('upload-data', 'filename')
)
def show_upload_dialog(content, n_clicks, filename):
    if not dash.callback_context.triggered[0]['value']:
        raise dash.exceptions.PreventUpdate
    trigger = dash.callback_context.triggered[0]['prop_id'].split('.')[0]

    header = dbc.ModalHeader(f"File Upload for {filename}"),

    if trigger == 'close-upload-diag':
        return False, header
    else:
        return True, header



@app.callback(
    Output('argument-detail-box', 'children'),
    Output('arg-table', 'data'),
    Output('algo-table', 'data'),
        Input('arg-table', 'active_cell'),
        Input('arg-table', 'dropdown'),
        Input('arg-table', 'data'),
        Input('algo-table', 'data'),
    State('argument-detail-box', 'children'),
)
def handle_input_table_change(active_cell, dropdown, arg_data, algo_data, details_children):
    """handle changes to input table.
    There are two scenarios how the argument details or the data for the algo
    table can change.
    First, another item is clicked. This changes the output of the detail box as
    well as the algorithm output. For the algorithm output, the similarity
    search is conducted and the data of the most similar items is put into the algo-table.
    Second, a category is deleted and the dropdown options change. When this
    happens, the algo-table and the arg-table have to clear the dropdown value
    of all the items that have this category selected.
    Third, a dropdown item is changed in either datatable (algo or arg). If
    that's the case, the change must be reflected in the other table as well.
    In this case, the details table should also be refreshed.
    Fourth Case is when the entire table has to be changed due to a file Upload.
    In this case, all data has to be reset.
    """
    if not dash.callback_context.triggered[0]['value']:
        raise dash.exceptions.PreventUpdate
    trigger = dash.callback_context.triggered[0]['prop_id']
    # first case.
    if trigger == 'arg-table.active_cell':
        details_table, algo_table_data = table_sync.active_cell_change(active_cell, arg_data, search_index, SIMILARITY_SEARCH_RESULTS)
        return details_table, arg_data, algo_table_data
    # second case.
    elif trigger == 'arg-table.dropdown':
        new_arg_data, new_algo_data =  table_sync.sync_categories(dropdown, arg_data, algo_data)
        return details_children, new_arg_data, new_algo_data
    # third case, arg-table data has changed.
    elif trigger in ['arg-table.data', 'algo-table.data']:
        return table_sync.sync_dropdown_selection(arg_data, algo_data, trigger, active_cell)



if __name__ == '__main__':
    app.run_server(debug=True)
