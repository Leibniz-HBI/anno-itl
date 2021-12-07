"""Functions for keeping the data tables in sync.

Since there can be only on callback for each Output, and the datatables can
change due to various inputs, it gets crowded pretty quickly. All callback
actions that change the data tables have their function here.
The functions only get the inputs that are actually changed. The Output that are
not changed by that action are returned by the callback.
"""

import pandas as pd
import html_generators
import datasets


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
        The dash html.components for the details table and the data for the
        similarity table
    """
    dff = pd.DataFrame(arg_data)
    sentence_data = dff.iloc[active_cell['row_id']]
    sentence = sentence_data['text unit']
    details_table = html_generators.create_details_table(sentence_data, header='argument details')
    similarity_indices = datasets.search_faiss_with_string(
        sentence,
        search_index,
        SIMILARITY_SEARCH_RESULTS
    )
    similarity_table_data = dff.iloc[similarity_indices].to_dict('records')
    return details_table, similarity_table_data


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


def sync_dropdown_selection(arg_data, algo_data, trigger, active_cell):
    """Syncs the selection of labels in both tables

    Based on the trigger, the values from the arg table are put into the algo
    table or vice versa. For the first case, a new slice of the arg table is
    created, for the second case, the values from the algo table are updated
    into the arg table.
    The details table is also refreshed, so that label changes are reflected
    immediately.
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
        algo_df =  arg_df.iloc[algo_df['id']]
    else:
        arg_df = arg_df.set_index('id')
        algo_df =algo_df.set_index('id')
        # update does not work with `None values`, therefore replace them before
        # updating and none them afterwards. Seems kinda hacky..
        algo_df.fillna('removed', inplace=True)
        arg_df.update(algo_df)
        algo_df.replace({'removed': None}, regex=True, inplace=True)
        arg_df.replace({'removed': None}, regex=True, inplace=True)
        arg_df = arg_df.reset_index()
        algo_df = algo_df.reset_index()
    sentence_data = arg_df.iloc[active_cell['row_id']]
    details_table = html_generators.create_details_table(sentence_data, header='argument details')
    return details_table, arg_df.to_dict('records'), algo_df.to_dict('records')
