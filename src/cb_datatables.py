"""Callbacks regarding the data tables
"""

import pandas as pd
from app import app
import dash
from dash.dependencies import Input, Output, State
from dash import dash_table
import dash.html as html

import datasets
# TODO: find a better place for these kind of settings.
SIMILARITY_SEARCH_RESULTS = 10


@app.callback(
    Output('arg-list-box', 'children'),
    Output('algo-box', 'children'),
    Input('current_dataset', 'data'),
)
def refresh_datatable(current_dataset):
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
    if not dash.callback_context.triggered[0]['value']:
        raise dash.exceptions.PreventUpdate
    header = html.Div(
        f'Text data of {current_dataset["project_name"]} ',
        id="arg-list-header"
    )
    df = pd.DataFrame(current_dataset['data'])
    label_name = f'{current_dataset["project_name"]}_label'
    labels = [lbl for lbl in df[label_name].unique() if lbl]
    columns = [
        {'name': 'Argument', 'id': 'text unit'},
        {'name': 'Label', 'id': f'{current_dataset["project_name"]}_label',
         'editable': True, 'presentation': 'dropdown'}
    ]
    dropdown = {
        f'{current_dataset["project_name"]}_label':
        {'options': [{'label': lbl, 'value': lbl} for lbl in labels]}
    }
    table = dash_table.DataTable(
        id='arg-table',
        filter_action="native",
        columns=columns,
        data=current_dataset['data'],
        dropdown=dropdown,
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
    )
    # it aint a bit....
    dirty_bit = html.Div(hidden=True, id='dirty-bit', **{'data-changed': 0})
    algo_header = html.Div('Similar Arguments', id="algo-box-header")
    algo_table = dash_table.DataTable(
        id='algo-table',
        columns=columns,
        dropdown=dropdown,
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
    )
    return [header, table, dirty_bit], [algo_header, algo_table]


@app.callback(
    Output('arg-table', 'dropdown'),
    Output('algo-table', 'dropdown'),
    Input('label-list', 'children'),
    State('current_dataset', 'data'),
)
def update_dropdown_options(label_list, current_dataset):
    """updates dropdown options for the datatables when the label list changes.
    The first element of the label list ist the label list header. Therefore the
    list comprehension `labels=...` starts at label_list index 1.

    Args:
        label_list ([type]): children from the label list
        current_dataset ([type]): current dataset info and data

    Returns:
        updated dropdown menus for both data tables.
    """
    if not dash.callback_context.triggered[0]['value']:
        raise dash.exceptions.PreventUpdate
    # the props children stuff is getting the value from html.H6 element of the
    # label card.
    labels = [list_item['props']['children'][1]['props']['children']
              for list_item in label_list[1:]]
    dropdown = {
        f'{current_dataset["project_name"]}_label': {
            'options': [{'label': lbl, 'value': lbl} for lbl in labels]
        }
    }
    return dropdown, dropdown


@app.callback(
    Output('arg-table', 'data'),
    Output('algo-table', 'data'),
    Output('dirty-bit', 'data-changed'),
    Input('arg-table', 'active_cell'),
    Input('arg-table', 'dropdown'),
    Input('arg-table', 'data'),
    Input('algo-table', 'data'),
    State('current_dataset', 'data'),
    State('dirty-bit', 'data-changed'),
)
def handle_input_table_change(
        active_cell, dropdown, arg_data,
        algo_data, current_dataset, n_data_changes):
    """handle changes to input table.
    There are a few scenarios how the data for the algo
    table can change.First, another item is clicked. This changes the output of
    the detail box as well as the algorithm output. For the algorithm output,
    the similarity search is conducted and the data of the most similar items
    is put into the algo-table.
    Second, a label is deleted and the dropdown options change. When this
    happens, the algo-table and the arg-table have to clear the dropdown value
    of all the items that have this label selected.
    Third, a dropdown item is changed in either datatable (algo or arg). If
    that's the case, the change must be reflected in the other table as well.
    It might be that there's no data in the algo table. In that case, no
    syncronization has to be done.
    Fourth Case is when the entire table has to be changed due to a file Upload
    or due to loading a new dataset
    In this case, the data of the algo table has to change and rest needs to be reset.
    """
    if not dash.callback_context.triggered[0]['value']:
        raise dash.exceptions.PreventUpdate
    trigger = dash.callback_context.triggered[0]['prop_id']
    # first case.
    if trigger == 'arg-table.active_cell':
        algo_table_data = active_cell_change(
            active_cell,
            arg_data,
            current_dataset['dataset_name'],
            SIMILARITY_SEARCH_RESULTS)
        return arg_data, algo_table_data, n_data_changes
    # second case.
    elif trigger == 'arg-table.dropdown':
        new_arg_data, new_algo_data = sync_labels(
            dropdown,
            arg_data,
            algo_data,
            current_dataset['project_name']
        )
        return new_arg_data, new_algo_data, n_data_changes + 1
    # third case, arg-table data has changed.
    elif trigger in ['arg-table.data', 'algo-table.data']:
        if algo_data:
            return sync_dropdown_selection(
                arg_data, algo_data, trigger,
                active_cell, n_data_changes
            )
        else:
            return arg_data, algo_data, n_data_changes + 1


def active_cell_change(active_cell, arg_data, search_index, SIMILARITY_SEARCH_RESULTS):
    """Provides similarity search and info data on cell click.

    When a text data from the arg-table is clicked, the similarity search is
    conducted and the argument info views is updated with the new data.

    Args:
        active_cell: active cell object of the cell that was selected
        arg_data: data from the arg-table
        search_index: faiss index for similarity search
        SIMILARITY_SEARCH_RESULTS: number of similarity search results

    Returns:
        The data for the similarity table
    """
    dff = pd.DataFrame(arg_data)
    sentence_data = dff.iloc[active_cell['row_id']]
    sentence = sentence_data['text unit']
    similarity_indices = datasets.search_faiss_with_string(
        sentence,
        search_index,
        SIMILARITY_SEARCH_RESULTS
    )
    similarity_table_data = dff.iloc[similarity_indices].to_dict('records')
    return similarity_table_data


def sync_dropdown_selection(arg_data, algo_data, trigger, active_cell, n_data_changes):
    """Syncs the selection of labels in both tables

    Based on the trigger, the values from the arg table are put into the algo
    table or vice versa. For the first case, a new slice of the arg table is
    created, for the second case, the values from the algo table are updated
    into the arg table.
    Args:
        arg_data : data from arg-table
        algo_data: data from algo_data
        trigger: the trigger value
        active_cell: the active cell object.

    Returns:
        The updated table data.
    """
    arg_df = pd.DataFrame(arg_data)
    algo_df = pd.DataFrame(algo_data)
    if trigger == 'arg-table.data':
        algo_df = arg_df.iloc[algo_df['id']]
    else:
        arg_df = arg_df.set_index('id')
        algo_df = algo_df.set_index('id')
        # update does not work with `None values`, therefore replace them before
        # updating and none them afterwards. Seems kinda hacky..
        algo_df.fillna('removed', inplace=True)
        arg_df.update(algo_df)
        algo_df.replace({'removed': None}, regex=True, inplace=True)
        arg_df.replace({'removed': None}, regex=True, inplace=True)
        arg_df = arg_df.reset_index()
        algo_df = algo_df.reset_index()
    return arg_df.to_dict('records'), algo_df.to_dict('records'), n_data_changes + 1


def sync_labels(dropdown, arg_data, algo_data, project_name):
    """Deletes label selections on label deletion from tables.

    The function goes through all rows of the datatables and sets the label
    of all rows with now deleted label back to `None`.

    Args:
        dropdown: dropdown options
        arg_data: data from the arg table
        algo_data: data from the algorithm table

    Returns:
        arg_data and algo_data with new label information
    """
    label_name = f'{project_name}_label'
    labels = [lbl['label'] for lbl in dropdown[label_name]['options']]
    for index, row in enumerate(arg_data):
        if row[label_name] not in labels:
            arg_data[index][label_name] = None
    for index, row in enumerate(algo_data):
        if row[label_name] not in labels:
            algo_data[index][label_name] = None
    return arg_data, algo_data
