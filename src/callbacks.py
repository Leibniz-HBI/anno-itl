"""Callbacks from the main layout.
Here are all callbacks that relate to the main layout and not to the project
opening modal or the data tables. They are in different files, but they all are
imported here in order to have them called
"""
import re
import pandas as pd
from app import app
import dash
from dash.dependencies import Input, Output, State, ALL
from dash import html

import datasets
import open_modal


@app.callback(
    Output('btn-save-data', 'disabled'),
    Input('dirty-bit', 'data-changed'),
    Input('clean-bit', 'data-saved'),
    Input('current_dataset', 'data')
)
def enable_save_button(data_changed, data_saved, current_dataset):
    if not dash.callback_context.triggered[0]['value']:
        raise dash.exceptions.PreventUpdate
    trigger = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
    if trigger == 'dirty-bit':
        return False
    else:
        return True


@app.callback(
    Output('clean-bit', 'data-saved'),
    Input('btn-save-data', 'n_clicks'),
    State('arg-table', 'data'),
    State('clean-bit', 'data-saved'),
    State('current_dataset', 'data'),
)
def save_data(n_clicks, current_table_data, clean_bit, current_dataset):
    if not dash.callback_context.triggered[0]['value']:
        raise dash.exceptions.PreventUpdate
    datasets.update_project_columns(
        current_table_data,
        current_dataset['project_name'],
        current_dataset['dataset_name']
    )
    return clean_bit + 1


@app.callback(
    Output('app-header', 'children'),
    Input('btn-new-data', 'n_clicks'),
    State('app-header', 'children'),
    State('current_dataset', 'data')
)
def load_data_diag(open_clicks, children, current_dataset):
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
    children.append(open_modal.open_project_modal(
        current_dataset['project_name'] if current_dataset else None)
    )
    return children


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
    if trigger in ['submit-lbl-button', 'lbl-input']:
        if label_input:
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
        button_id = int(re.findall(r'\d+', trigger)[0])
        for child in children:
            if child['props']['children'][1]['props']['id']['index'] == button_id:
                children.remove(child)
    return children
