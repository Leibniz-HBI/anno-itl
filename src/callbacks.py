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
import dash_bootstrap_components as dbc

import datasets
import open_modal
from layout import label_list_header


@app.callback(
    Output('btn-save-data', 'disabled'),
    Input('dirty-bit', 'data-changed'),
    Input('clean-bit', 'data-saved'),
    Input('current_dataset', 'data')
)
def enable_save_button(data_changed, data_saved, current_dataset):
    """Enables/disables the save button.

    The button only needs to be enabled if the dirty bit is changed. If a new
    dataset is loaded, or changes are saved, the button is disabled.
    """
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
    State('label-list', 'children'),
    State('current_dataset', 'data'),
)
def save_data(n_clicks, current_table_data, clean_bit, label_list, current_dataset):
    """Saves the changes to the project.

    Afterwards the clean bit is increased to signal that the data was stored.
    """
    if not dash.callback_context.triggered[0]['value']:
        raise dash.exceptions.PreventUpdate
    datasets.update_project_columns(
        current_table_data,
        current_dataset['project_name'],
        current_dataset['dataset_name']
    )
    labels =[label['props']['id']['label'] for label in label_list[1:]]
    datasets.save_labels(current_dataset['project_name'], labels)
    return clean_bit + 1


@app.callback(
    Output('modal-container', 'children'),
    Input('btn-new-data', 'n_clicks'),
    State('current_dataset', 'data')
)
def load_data_diag(open_clicks, current_dataset):
    """Opens new dataset modal.

    It opens inside a hidden div modal container. When the "open or create
    project" button is pressed again, a new modal is created. This can then
    easily populate the dropdown menues again, plus it has the advantage that
    opening the modal can be done in a different output than closing.

    Args:
        open_click: input button clikcs
        children ([type]): children of header

    Returns:
        children of header with new modal.
    """
    if not dash.callback_context.triggered[0]['value']:
        raise dash.exceptions.PreventUpdate
    return open_modal.open_project_modal(
        current_dataset['project_name'] if current_dataset else None)


def create_label_card(label, index):
    """Creates the label card for a label.
    The index is important for pattern matching callbacks. It is not only put on
    the button but also on the card itselve, so that check for the index is not
    so long. (so you can use ['props']['id']['index'] instead of going down to
    the button.)
    The label is part of the `id` dict for a similar reason

    Args:
        label: label name
        index: position of the card in the list of cards.

    Returns:
        [type]: dbc.Card with the stuff needed.
    """
    card = dbc.Card([
        dbc.Button(
            className="bi bi-x py-0 px-1 position-absolute top-0 end-0 border-0",
            id={'type': 'label-remove-btn', 'index': index},
            style={'color': 'white', 'height': '100%', 'background': 'red'},
        ),
        html.H6(label, className='card-title')],
        class_name="py-1 px-3",
        id={'type': 'label-card', 'index': index, 'label': label},
        className="mb-0"
    )
    return card


@app.callback(
    Output('label-list', 'children'),
    Input('submit-lbl-button', 'n_clicks'),
    Input("lbl-input", "n_submit"),
    Input({'type': 'label-remove-btn', 'index': ALL}, 'n_clicks'),
    Input('current_dataset', 'data'),
    State('lbl-input', 'value'),
    State('label-list', 'children'),
)
def add_label(n_clicks, n_submit, remove_click, current_dataset, label_input, children):
    """Handle Label input.
    Data from the input box can be submitted with enter and button click. If
    that happens, a new label will be created if it doesn't exist yet.
    If the remove button of a label is presesd, the corresponding list
    element will be deleted.

    When iterating over the children of the label-list, the first element is
    omitted because it's the header. The header exists not only for aesthetics
    (which, of course, are top notch!) but also because callbacks which have
    label-list, children as an input are not triggered when no elements of
    label-list are still printed to the screen. Therefore they don't trigger
    when the label-list is in fact empty and thus not printed.
    """
    if not dash.callback_context.triggered[0]['value']:
        raise dash.exceptions.PreventUpdate
    trigger = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
    if trigger in ['submit-lbl-button', 'lbl-input']:
        if label_input:
            already_there = False
            for label in children[1:]:
                if label_input == label['props']['id']['label']:
                    already_there = True
            if not already_there:
                children.append(create_label_card(label_input, len(children)))
    elif trigger == 'current_dataset':
        children = [label_list_header]
        labels = datasets.load_labels(current_dataset['project_name'])
        for index, lbl in enumerate(labels):
            children.append(create_label_card(lbl, index))
    else:
        button_id = int(re.findall(r'\d+', trigger)[0])
        # don't iterate over header
        for child in children[1:]:
            if child['props']['id']['index'] == button_id:
                children.remove(child)
    return children
