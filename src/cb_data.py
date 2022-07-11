"""Callbacks regarding the data tables
"""

from app import app
from dash.exceptions import PreventUpdate
from dash import html, Input, Output, State, MATCH, ALL, ctx
from data_layout import create_label_pill
import dash_bootstrap_components as dbc


import datasets
import data_layout
# TODO: find a better place for these kind of settings.
SIMILARITY_SEARCH_RESULTS = 10


@app.callback(
    Output('text-unit-view', 'children'),
    Input('current_dataset', 'data'),
    prevent_initial_call=True
)
def fill_text_unit_view(current_dataset):
    """Create Datatables after load.

    A change of the current_dataset means, that the user has loaded another
    project. If that happens, it's easiest to just create new Datatables
    altogether, due to the fact that column ids have to change (underlying
    data has different column names!).


    Args:
        current_dataset: the new current_datasets dictionary

    Returns:
       new arguments table and a new, blank algorithm table. It's still
       recreated, so that it has the correct column ids
    """
    if not ctx.triggered[0]['value']:
        raise PreventUpdate
    header = dbc.Row(
        dbc.Col([
            dbc.Button("fetch new data", className="float-start"),
            html.H5(f'Text data of {current_dataset["project_name"]}', className="text-center"),
        ],
            id="text-unit-header",
            class_name="mb-1"
        )
    )
    children = [header]
    data, text_column = datasets.fetch_data_slice(current_dataset['project_name'])
    label_key = f'{current_dataset["project_name"]}_label'
    labels = datasets.load_labels(current_dataset['project_name'])
    children.extend([
        data_layout.create_data_card(text_unit, labels, label_key, text_column)
        for text_unit in data])
    # it aint a bit....
    dirty_bit = html.Div(hidden=True, id='dirty-bit', **{'data-changed': 0, 'data-labelchanged': 0})
    children.append(dirty_bit)
    return children


@app.callback(
    Output({'type': 'add-lbl-collapse', 'index': MATCH}, 'is_open'),
    Input({'type': 'tu-open-label-collapse', 'index': MATCH}, 'n_clicks'),
    State({'type': 'add-lbl-collapse', 'index': MATCH}, 'is_open'),
    prevent_initial_call=True
)
def open_collapse(button, is_open):
    return not is_open


@app.callback(
    output=dict(
        options=Output({'type': 'tu-label-select', 'index': ALL}, 'options')
    ),
    inputs=Input('label-list', 'children'),
    prevent_initial_call=True
)
def update_label_options(label_list):
    """updates  options for the label selection when the label list changes.
    The first element of the label list ist the label list header. Therefore the
    list comprehension `labels=...` starts at label_list index 1.

    Args:
        label_list: children from the label list
        current_dataset: current dataset info and data

    Returns:
        updated radio options.
    """
    # the props children stuff is getting the value from html.H6 element of the
    # label card.
    labels = [list_item['props']['children'][1]['props']['children']
              for list_item in label_list[1:]]
    outputs = len(ctx.outputs_grouping['options'])
    options = [{"label": label, "value": label} for label in labels]
    return {'options': [options for _ in range(outputs)]}


@app.callback(
    Output({'type': 'tu-footer', 'index': MATCH}, 'children'),
    Input({'type': 'tu-label-select', 'index': MATCH}, 'value'),
    prevent_initial_call=True
)
def add_label_to_text(label):
    if not label:
        raise PreventUpdate
    if ctx.triggered:
        index = ctx.triggered_id['index']
    return create_label_pill(label, index)


@app.callback(
    Output('dirty-bit', 'data-changed'),
    Input({'type': 'tu-footer', 'index': ALL}, 'children'),
    State('dirty-bit', 'data-changed'),
    prevent_initial_call=True
)
def trigger_data_change(happening, dirty_bit):
    return dirty_bit + 1
