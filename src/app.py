"""Dash application for annotation of short text usign custom labels and
giving suggestions for similar text units.
"""

from os import terminal_size
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
import table_sync
import open_modal

app = dash.Dash(external_stylesheets=[dbc.themes.JOURNAL],
                suppress_callback_exceptions=True
                )

SIMILARITY_SEARCH_RESULTS = 10


app.layout = html.Div([
    html.Div(
        id='app-header',
        children=[
            html.Div('Annotation tool with Human in the Loop', id="app-header-title"),
            dbc.Button("Open or create project", color='primary', id='btn-new-data'),
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
                        {'name': 'Label', 'id': 'label', 'editable': True, 'presentation': 'dropdown'}
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
        id="label-pane",
        children=[
            html.Div(id="label-box", children=[
                html.Div(
                    id="label-header",
                    children=[
                        dbc.Input(id='lbl-input', placeholder='Add Label..', type='text'),
                        dbc.Button(id='submit-lbl-button', color='primary', n_clicks=0, children='Add')
                    ]),
                html.Ul(
                    id='label_list',
                    children=[
                    ])
                ]
            ),
            html.Div(id='algo-box', children=[
                html.Div('Similar Arguments', id="algo-box-header"),
                dash_table.DataTable(
                    id='algo-table',
                    columns=[
                        {'name': 'Argument', 'id': 'text unit'},
                        {'name': 'Label', 'id': 'label',  'editable':True, 'presentation': 'dropdown'}
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
    Output('arg-table', 'dropdown'),
    Output('algo-table', 'dropdown'),
    Input('label_list', 'children'),
    State('current_dataset', 'data'),
)
def update_dropdown_options(label_list, current_dataset):

    labels = [list_item['props']['children'][0] for list_item in label_list]
    dropdown = {
    f'{current_dataset["project_name"]}_label': {
        'options': [{'label': lbl, 'value': lbl} for lbl in labels]
    }
    }
    return dropdown, dropdown

@app.callback(
    Output('label_list', 'children'),
    Input('submit-lbl-button', 'n_clicks'),
    Input("lbl-input", "n_submit"),
    Input({'type': 'label-remove-btn', 'index': ALL}, 'n_clicks'),
    Input('current_dataset', 'data'),
    State('lbl-input', 'value'),
    State('label_list', 'children'),
)
def add_label(n_clicks, n_submit, remove_click, current_dataset, label_input, children):
    """Handle Label input.
    Data from the input box can be submitted with enter and button click. If
    that happens, a new label will be created if it doesn't exist yet.
    If the remove button of a label is presesd, the corresponding list
    element will be deleted.
    """
    if not dash.callback_context.triggered[0]['value']:
        raise dash.exceptions.PreventUpdate
    trigger = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
    if trigger in ['submit-lbl-button', 'lbl-input'] and label_input:
        already_there = False
        for label in children:
            if label_input in label['props']['children']:
                already_there = True
        if not already_there:
            new_cat = html.Li(
                children=[
                    label_input,
                    html.Button(
                        'remove',
                        id={'type': 'label-remove-btn', 'index': len(children)})
                ],
                id={'type': 'label-item', 'index': len(children)},
                className="label-container")
            children.append(new_cat)
    elif trigger == 'current_dataset':
        tmp_df = pd.DataFrame(current_dataset['data'])
        label_name = f'{current_dataset["project_name"]}_label'
        if label_name in tmp_df:
            labels = [lbl for lbl in tmp_df[label_name].unique() if lbl]
            children = [html.Li(
                children=[
                    lbl,
                    html.Button(
                        'remove',
                        id={'type': 'label-remove-btn', 'index': index})
                ],
                id={'type': 'label-item', 'index': index},
                className="label-container") for index, lbl in enumerate(labels)]
    else:
        button_id = int(re.findall('\d+', trigger)[0])
        for child in children:
            if child['props']['children'][1]['props']['id']['index'] == button_id:
                children.remove(child)
    return children


@app.callback(
    Output('app-header', 'children'),
    Input('btn-new-data', 'n_clicks'),
    State('app-header', 'children'),
)
def load_data_diag(open_clicks, children):
    """adds and opens new dataset modal

    If there is an old modal, it is deleted.

    Args:
        open_click: input button clikcs
        children ([type]): children of header

    Returns:
        children of header with new modal.
    """
    if not dash.callback_context.triggered[0]['value']:
        raise dash.exceptions.PreventUpdate
    children = [child for child in children if child['props']['id'] != 'manage-datasets-modal']
    children.append(open_modal.open_project_modal())
    return children


@app.callback(
    Output('argument-detail-box', 'children'),
    Output('arg-table', 'data'),
    Output('algo-table', 'data'),
    Input('arg-table', 'active_cell'),
    Input('arg-table', 'dropdown'),
    Input('arg-table', 'data'),
    Input('algo-table', 'data'),
    State('current_dataset', 'data'),
    State('argument-detail-box', 'children'),
)
def handle_input_table_change(
        active_cell, dropdown, arg_data,
        algo_data, current_dataset, details_children):
    """handle changes to input table.
    There are a few scenarios how the argument details or the data for the algo
    table can change.
    First, another item is clicked. This changes the output of the detail box as
    well as the algorithm output. For the algorithm output, the similarity
    search is conducted and the data of the most similar items is put into the algo-table.
    Second, a label is deleted and the dropdown options change. When this
    happens, the algo-table and the arg-table have to clear the dropdown value
    of all the items that have this label selected.
    Third, a dropdown item is changed in either datatable (algo or arg). If
    that's the case, the change must be reflected in the other table as well.
    In this case, the details table should also be refreshed. It might be that
    there's no data in the algo table. In that case, no syncronization has to be
    done.
    Fourth Case is when the entire table has to be changed due to a file Upload
    or due to loading a new dataset
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
        new_arg_data, new_algo_data = table_sync.sync_labels(
            dropdown,
            arg_data,
            algo_data,
            current_dataset['project_name']
        )
        return details_children, new_arg_data, new_algo_data
    # third case, arg-table data has changed.
    elif trigger in ['arg-table.data', 'algo-table.data']:
        if algo_data:
            return table_sync.sync_dropdown_selection(arg_data, algo_data, trigger, active_cell)
        else:
            return details_children, arg_data, algo_data

@app.callback(
    Output('dataset-name-invalid-message', 'children'),
    Output('ds-name-input', 'valid'),
    Output('ds-name-input', 'invalid'),
    Input('ds-name-input', 'value')
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
        if datasets.check_name_exists(name):
            return "Name already taken", False, True
        else:
            return "not displayed", True, False


@app.callback(
    Output('dataset-description-invalid-message', 'children'),
    Output('ds-description-input', 'valid'),
    Output('ds-description-input', 'invalid'),
    Input('ds-description-input', 'value')
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
    Output('ds-text-unit-dd', 'disabled'),
    Output('ds-text-unit-dd', 'options'),
    Output('ds-project-label-selection-dd', 'options'),
    Input('dataset-file-input', 'contents'),
    State('dataset-file-input', 'filename'),
)
def validate_dataset_upload(upload, filename):
    if not dash.callback_context.triggered[0]['value']:
        raise dash.exceptions.PreventUpdate
    valid_file_endings = ['.xls', '.csv', '.ctv']
    if not filename[-4:] in valid_file_endings:
        return 'danger', 'Not a valid File type', {}, True, [], []
    df = datasets.parse_contents(upload, filename)
    if df is not None:
        options = [{'label': key, 'value': key} for key in df.keys()]
        label_options = [{'label': f'{key} ({df[key].nunique()} unique items)', 'value': key} for key in df.keys()]
        return 'success', 'Dataset valid', df.to_dict('records'), False, options, label_options
    else:
        return 'danger', 'File was not readable', {}, True, [], []


@app.callback(
    Output('ds-project-label-selection-dd', 'disabled'),
    Input('ds-project-label-checkbox', 'value'),
    Input('ds-project-label-selection-dd', 'options')
)
def change_add_label_selection_enabled_status(checked, options):
    if options and checked:
        return False
    else:
        return True


@app.callback(
    Output('create-project-label-selection-dd', 'options'),
    Input('create-project-dd', 'value')
)
def get_label_options(dataset):
    if not dash.callback_context.triggered[0]['value']:
        raise dash.exceptions.PreventUpdate

    columns = datasets.get_dataset_labels(dataset)
    options = [{'label': f'{key[0]} ({key[1]} unique items)', 'value': key} for key in columns]
    return [{'label': f'{key[0]} ({key[1]} unique items)', 'value': key[0]} for key in columns]


@app.callback(
    Output('create-project-label-selection-dd', 'disabled'),
    Input('create-project-label-checkbox', 'value'),
    Input('create-project-label-selection-dd', 'options')
)
def change_add_label_selection_enabled_status(checked, options):
    if options and checked:
        return False
    else:
        return True


@app.callback(
    Output('add-validator', 'data-upload-valid'),
    Output('submit-text', 'children'),
    Output('submit-text', 'color'),
    Input('add-dataset-btn', 'n_clicks'),
    State('ds-name-input', 'valid'),
    State('ds-description-input', 'valid'),
    State('new_data', 'data'),
    State('ds-project-checkbox', 'value'),
    State('new-ds-proj-name', 'valid'),
    State('ds-text-unit-dd', 'value'),
    State('ds-project-label-selection-dd', 'value'),
    State('ds-project-label-checkbox', 'value'),
)
def ds_add_validation(
        n_clicks, name_valid, desc_valid, new_data,
        project_name_checked, project_name_valid,
        text_unit_selection, proj_label_selection, label_checked):
    if not dash.callback_context.triggered[0]['value']:
        raise dash.exceptions.PreventUpdate
    validators = [name_valid, desc_valid, new_data, text_unit_selection]
    invalid_item_names = ['name', 'description', 'uploaded data', 'text column selection']
    if project_name_checked:
        validators.append(project_name_valid)
        invalid_item_names.append('project name')
    if label_checked:
        validators.append(proj_label_selection)
        invalid_item_names.append('label column')
    if all(validators):
        return True, 'success', 'success'
    else:
        invalid_items = [name for name, bool in zip(invalid_item_names, validators) if not bool]
        error_message = f"""check your input! The following input{'s' if len(invalid_items)>1 else ''}
        {'were' if len(invalid_items)>1 else 'is'} not valid: {', '.join(invalid_items)}"""
        return False, error_message, 'danger'


@app.callback(
    Output('create-validator', 'data-create-valid'),
    Output('proj-create-text', 'children'),
    Output('proj-create-text', 'color'),
    Input('create-project-btn', 'n_clicks'),
    State('create-proj-name', 'valid'),
    State('create-project-label-checkbox', 'value'),
    State('create-project-label-selection-dd', 'value'),
    State('create-project-dd', 'value')

)
def proj_create_validation(n_clicks, name_valid, label_checked, label_selection, proj_selection):
    if not dash.callback_context.triggered[0]['value']:
        raise dash.exceptions.PreventUpdate
    validators = [name_valid, proj_selection]
    invalid_item_names = ['Project name', 'Project Selection']
    if label_checked:
        validators.append(label_selection)
        invalid_item_names.append('Label Selection')
    if all(validators):
        return True, 'success', 'success'
    else:
        invalid_items = [name for name, bool in zip(invalid_item_names, validators) if not bool]
        error_message = f"""check your input! The following input{'s' if len(invalid_items)>1 else ''}
        {'were' if len(invalid_items)>1 else 'is'} not valid: {', '.join(invalid_items)}"""
        return False, error_message, 'danger'


@app.callback(
    Output('create-proj-name-invalid-message', 'children'),
    Output('create-proj-name', 'valid'),
    Output('create-proj-name', 'invalid'),
    Input('create-proj-name', 'value')
)
def validate_create_project_name(name):
    if not dash.callback_context.triggered[0]['value']:
        raise dash.exceptions.PreventUpdate
    if len(name) < 4:
        return "not displayed", False, False
    pattern = re.compile(r"^[a-zA-Z0-9_]{4,30}$")
    valid = True if pattern.match(name) else False
    if not valid:
        return "Name not valid", False, True
    else:
        if datasets.check_name_exists(name, dataset=False):
            return "Name already taken", False, True
        else:
            return "not displayed", True, False


@app.callback(
    Output('manage-datasets-modal', 'is_open'),
    Output('current_dataset', 'data'),

    Input('add-validator', 'data-upload-valid'),
    Input('create-validator', 'data-create-valid'),
    Input('open-project-btn', 'n_clicks'),
    Input('close-upload-btn', 'n_clicks'),

    State('new_data', 'data'),
    State('current_dataset', 'data'),

    State('ds-name-input', 'value'),
    State('ds-description-input', 'value'),
    State('ds-text-unit-dd', 'value'),
    State('ds-project-label-selection-dd', 'value'),
    State('ds-project-label-checkbox', 'value'),

    State('new-ds-proj-name', 'value'),
    State('ds-project-checkbox', 'value'),

    State('create-project-dd', 'value'),
    State('create-proj-name', 'value'),
    State('create-proj-name', 'valid'),
    State('create-project-label-checkbox', 'value'),
    State('create-project-label-selection-dd', 'value'),

    State('open-project-dd', 'value')
)
def finalize_data_dialogue(
        add_valid, create_valid, open_button, close_button,
        new_data, current_dataset,
        ds_name, ds_description, ds_text_unit_selection, ds_label_selection, label_checked,
        ds_project_name, ds_project_name_checked,
        create_proj_dd_selection, create_project_name,create_project_name_valid,
        create_label_checked, create_proj_label_selection,
        open_project_dd_selection):
    """Creates Dataset (and project, if checked) or closes dialogue.

    First it is checked which button trigger the function. If it's the close
    button (close-upload-btn), just close the modal and return the Input States
    of the loaded datast.
    The other option are:
    1. The Create!-Button (add-dataset-btn), for adding a new data set.
    2. The Create Project button (create-project-btn) for creating a project
       from an existing dataset.
    3. The Open Project for (open-project-btn) for opening en existing project.

    """
    if not dash.callback_context.triggered[0]['value']:
        raise dash.exceptions.PreventUpdate
    trigger = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
    if trigger == 'close-upload-btn':
        return False, current_dataset
    elif trigger == 'add-validator':
        return open_modal.add_dataset_cb(
            new_data, ds_project_name_checked,
            ds_name, ds_text_unit_selection, ds_label_selection if label_checked else False,
            ds_description, ds_project_name, current_dataset
        )
    elif trigger == 'create-validator':
        return open_modal.create_project_cb(
            create_project_name_valid, create_proj_dd_selection,
            create_project_name, current_dataset, create_proj_label_selection if create_label_checked else False
        )
    elif trigger == 'open-project-btn':
        if open_project_dd_selection:
            return open_modal.open_project_cb(open_project_dd_selection)
        else:
            return True, current_dataset


@app.callback(
    Output('arg-list-box', 'children'),
    Output('algo-table', 'columns'),
    Input('current_dataset', 'data'),
)
def refresh_datatable(current_dataset):
    if not dash.callback_context.triggered[0]['value']:
        raise dash.exceptions.PreventUpdate
    header = html.Div(
        f'Text data of {current_dataset["project_name"]} ',
        id="arg-list-header"
    )
    columns=[
        {'name': 'Argument', 'id': 'text unit'},
        {'name': 'Label', 'id': f'{current_dataset["project_name"]}_label', 'editable': True, 'presentation': 'dropdown'}
    ]
    table = dash_table.DataTable(
        id='arg-table',
        filter_action="native",
        columns=columns,
        data=current_dataset['data'],
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
    )
    return [header, table], columns

@app.callback(
    Output('new-ds-proj-name-invalid-message', 'children'),
    Output('new-ds-proj-name', 'valid'),
    Output('new-ds-proj-name', 'invalid'),
    Input('new-ds-proj-name', 'value')
)
def validate_ds_project_name(name):
    if not dash.callback_context.triggered[0]['value']:
        raise dash.exceptions.PreventUpdate
    if len(name) < 4:
        return "not displayed", False, False
    pattern = re.compile(r"^[a-zA-Z0-9_]{4,30}$")
    valid = True if pattern.match(name) else False
    if not valid:
        return "Name not valid", False, True
    else:
        if datasets.check_name_exists(name, dataset=False):
            return "Name already taken", False, True
        else:
            return "not displayed", True, False


@app.callback(
    Output('new-ds-proj-name', 'disabled'),
    Input('ds-project-checkbox', 'value')
)
def check_project_creation_input(checked):
    """Enables/Disables the input field for project name.

    Based on the value of the coresponding Checkbox, the input is either enabled
    or disabled.

    Args:
        checked: Value of the project checkbox

    Returns:
        Value for 'disabled' property of project name input.
    """
    return not checked


if __name__ == '__main__':
    app.run_server(debug=True)
