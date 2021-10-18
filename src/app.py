"""Dash application for annotation of short text usign custom categories and
giving suggestions for similar text units.
"""

import re
import json
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
                suppress_callback_exceptions=True
                )

SIMILARITY_SEARCH_RESULTS = 10


app.layout = html.Div([
    html.Div(
        className='app-header',
        id='app-header',
        children=[
            html.Div('Annotation tool with Human in the Loop', className="app-header--title"),
            dbc.Button("Open or create project", color='primary', id='btn-new-data'),
        ]
    ),
    html.Div(
        className="arg-list-pane",
        children=[
            dcc.Store(id='current_dataset'),
            dcc.Store(id='new_data'),
            html.Div(hidden=True, **{'data-new-dataset': 0}, id='loaded-new-dataset'),
            html.Div(className="arg-list-box", children=[
                html.Div('Argument Input', className="arg-list-header"),
                dash_table.DataTable(
                    id='arg-table',
                    filter_action="native",
                    columns=[
                        {'name': 'Argument', 'id': 'text unit'},
                        {'name': 'Category', 'id': 'category', 'editable': True, 'presentation': 'dropdown'}
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
                        {'if': {'column_id': 'text unit'},
                            'textOverflow': 'ellipsis',
                            'maxWidth': 0,
                            'width': '90%',
                            'textAlign': 'left'
                            # 'cursor': 'pointer'
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
                    ])
                ]
            ),
            html.Div( id='algo-box', children=[
                html.Div('Similar Arguments', className="algo-box-header"),
                dash_table.DataTable(
                    id='algo-table',
                    columns=[
                        {'name': 'Argument', 'id': 'text unit'},
                        {'name': 'Category', 'id': 'category',  'editable':True, 'presentation': 'dropdown'}
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
                        {'if': {'column_id': 'text unit'},
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
    Input('loaded-new-dataset', 'data-new-dataset'),
    State('cat-input', 'value'),
    State('cat_list', 'children'),
    State('arg-table', 'dropdown'),
    State('algo-table', 'dropdown'),
    State('new_data', 'data')
)
def add_category(n_clicks, n_submit, remove_click, n_dataset_loads, cat_input, children, arg_dropdown, algo_dropdown, new_data):
    """Handle Category input.
    Data from the input box can be submitted with enter and button click. If
    that happens, a new category will be created if it doesn't exist yet.
    If the remove button of a category is presesd, the corresponding list
    element will be deleted.
    """
    if not dash.callback_context.triggered[0]['value']:
        raise dash.exceptions.PreventUpdate
    trigger = dash.callback_context.triggered[0]['prop_id']
    if trigger.split('.')[0] in ['submit-cat-button', 'cat-input'] and cat_input:
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
            if arg_dropdown:
                arg_dropdown['category']['options'] = arg_dropdown['category']['options'] + [{'label': cat_input, 'value': cat_input}]
                algo_dropdown = arg_dropdown
            else:
                arg_dropdown = {'category': {
                                    'options': [{'label': cat_input, 'value': cat_input}]
                                    }
                                }
                algo_dropdown = arg_dropdown
    elif trigger.split('.')[0] == 'loaded-new-dataset':
        tmp_df = pd.DataFrame(new_data)
        if 'category' in tmp_df:
            categories = [cat for cat in tmp_df['category'].unique() if cat]
            children = [html.Li(
                children=[
                    cat,
                    html.Button(
                        'remove',
                        id={'type': 'category-remove-btn', 'index': index})
                ],
                id={'type': 'category-item', 'index': index},
                className="category-container") for index, cat in enumerate(categories)]
            arg_dropdown = {
                'category': {
                    'options': [{'label': cat, 'value': cat} for cat in categories]
                }
            }
            algo_dropdown = arg_dropdown
    else:
        button_id = int(re.findall('\d+', trigger)[0])
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
    State('upload-data', 'filename'),
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
    Input('current_dataset', 'data'),
    State('new_data', 'data'),
    State('argument-detail-box', 'children'),
    State('loaded-new-dataset', 'data-new-dataset')
)
def handle_input_table_change(
        active_cell, dropdown, arg_data,
        algo_data, current_dataset, new_data, details_children, n_loaded_datasets ):
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
    In this case, the details table should also be refreshed. It might be that
    there's no data in the algo table. In that case, no syncronization has to be
    done.
    Fourth Case is when the entire table has to be changed due to a file Upload.
    In this case, the data of the algo table has to change and rest needs to be reset.
    """
    if not dash.callback_context.triggered[0]['value']:
        raise dash.exceptions.PreventUpdate
    trigger = dash.callback_context.triggered[0]['prop_id']
    # first case.
    if trigger == 'arg-table.active_cell':
        details_table, algo_table_data = table_sync.active_cell_change(
            active_cell,
            arg_data,
            current_dataset['dataset_name'],
            SIMILARITY_SEARCH_RESULTS)
        return details_table, arg_data, algo_table_data
    # second case.
    elif trigger == 'arg-table.dropdown':
        new_arg_data, new_algo_data = table_sync.sync_categories(
            dropdown,
            arg_data,
            algo_data)
        return details_children, new_arg_data, new_algo_data
    # third case, arg-table data has changed.
    elif trigger in ['arg-table.data', 'algo-table.data']:
        if algo_data:
            return table_sync.sync_dropdown_selection(arg_data, algo_data, trigger, active_cell)
        else:
            return details_children, arg_data, algo_data
    # fourth case load new dataset
    elif trigger == 'current_dataset.data':
        return [], new_data, []


@app.callback(
    Output('dataset-name-invalid-message', 'children'),
    Output('dataset-name-input', 'valid'),
    Output('dataset-name-input', 'invalid'),
    Input('dataset-name-input', 'value')
)
def validate_dataset_name_creation(name):
    if not dash.callback_context.triggered[0]['value']:
        raise dash.exceptions.PreventUpdate
    if len(name) < 4:
        return "not displayed", False, False
    pattern = re.compile(r"^[a-zA-Z0-9_]{4,30}$")
    valid = True if pattern.match(name) else False
    if not valid:
        return "Name not valid", False, True
    else:
        if datasets.check_dataset_exists(name):
            return "Name already taken", False, True
        else:
            return "not displayed", True, False


@app.callback(
    Output('dataset-description-invalid-message', 'children'),
    Output('dataset-description-input', 'valid'),
    Output('dataset-description-input', 'invalid'),
    Input('dataset-description-input', 'value')
)
def validate_dataset_desc_creation(description):
    if not dash.callback_context.triggered[0]['value']:
        raise dash.exceptions.PreventUpdate
    if len(description) < 10:
        return "not displayed", False, False
    pattern = re.compile(r"^[a-zA-Z0-9_äÄÖöÜüß ,!.?]{10,500}$")
    valid = True if pattern.match(description) else False
    if not valid:
        return "Description not valid", False, True
    else:
        return "not displayed", True, False


@app.callback(
    Output('dataset-upload-button', 'color'),
    Output('dataset-load-spinner', 'children'),
    Output('new_data', 'data'),
    Input('dataset-file-input', 'contents'),
    State('dataset-file-input', 'filename'),
)
def validate_dataset_upload(upload, filename):
    if not dash.callback_context.triggered[0]['value']:
        raise dash.exceptions.PreventUpdate
    valid_file_endings = ['.xls', '.csv', '.ctv']
    if not filename[-4:] in valid_file_endings:
        return 'danger', 'Not a valid File type', {}
    df = datasets.parse_contents(upload, filename)
    if df is not None:
        if 'text unit' in df.columns:
            if 'category' not in df:
                df['category'] = None
            if 'id' not in df:
                df.insert(0, 'id', df.index)
            return 'success', 'Dataset valid', df.to_dict('records')
        else:
            return 'danger', 'File does not contain column named text unit', {}
    else:
        'danger', 'File was not readable', {}


@app.callback(
    Output('manage-datasets-modal', 'is_open'),
    Output('current_dataset', 'data'),
    Output('loaded-new-dataset', 'data-new-dataset'),
    Input('add-dataset-button', 'n_clicks'),
    Input('close-upload-diag', 'n_clicks'),
    State('dataset-name-input', 'valid'),
    State('dataset-description-input', 'valid'),
    State('new_data', 'data'),
    State('dataset-name-input', 'value'),
    State('dataset-description-input', 'value'),
    State('current_dataset', 'data'),
    State('loaded-new-dataset', 'data-new-dataset')
)
def finalize_data_dialogue(add_button, close_button, name_valid, desc_valid, new_data, name, description, current_dataset, n_dataset_loads):
    if not dash.callback_context.triggered[0]['value']:
        raise dash.exceptions.PreventUpdate
    trigger = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
    if trigger == 'add-dataset-button':
        if name_valid and desc_valid and new_data:
            print(f'type from store is {type(new_data)}',)
            datasets.create_dataset(new_data, name, description)
            return False, {'dataset_name': name}, n_dataset_loads + 1
        else:
            return True, current_dataset, n_dataset_loads
    else:
        return False , {}, n_dataset_loads






if __name__ == '__main__':
    app.run_server(debug=True)
