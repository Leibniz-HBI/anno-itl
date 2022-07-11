"""Callbacks from the main layout.
Here are all callbacks that relate to the main layout and not to the project
opening modal or the data tables. They are in different files, but they all are
imported here in order to have them called
"""
from app import app
from dash import html, Input, Output, State, ALL, ctx
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import datasets
import open_modal
from layout import label_list_header


@app.callback(
    Output('btn-save-data', 'disabled'),
    inputs={
        "all_inputs": {
            "data_changed": Input('dirty-bit', 'data-changed'),
            "label_changed": Input('dirty-bit', 'data-labelchanged'),
            "data_saved": Input('clean-bit', 'data-saved'),
            "current_dataset": Input('current_dataset', 'data')
        }
    },
    prevent_initial_call=True
)
def enable_save_button(all_inputs):
    """Enables/disables the save button.

    The button only needs to be enabled if the dirty bit is changed. If a new
    dataset is loaded, or changes are saved, the button is disabled.
    """
    if ctx.triggered_id == 'dirty-bit':
        return False
    else:
        return True


@app.callback(
    Output('clean-bit', 'data-saved'),
    inputs={'n_clicks': Input('btn-save-data', 'n_clicks')},
    state={
        'clean_bit': State('clean-bit', 'data-saved'),
        'label_list': State('label-list', 'children'),
        'current_dataset': State('current_dataset', 'data'),
        'label_footers': State({'type': 'tu-footer', 'index': ALL}, 'children'),
    },
    prevent_initial_call=True
)
def save_data(n_clicks, clean_bit, label_list, current_dataset, label_footers):
    """Saves the changes to the project.

    Afterwards the clean bit is increased to signal that the data was stored.
    """
    # datasets.update_project_columns(
    #    current_table_data,
    #   current_dataset['project_name'],
    #     current_dataset['dataset_name']
    # )
    label_state = []
    for footer in label_footers:
        if isinstance(footer, dict):
            index = footer["props"]["id"]["index"]
            label = footer["props"]["id"]["label"]
            label_state.append((index, label))
    datasets.save_project_changes(label_state, current_dataset['project_name'])
    labels = [label['props']['id']['label'] for label in label_list[1:]]
    datasets.save_labels(current_dataset['project_name'], labels)
    return clean_bit + 1


@app.callback(
    Output('modal-container', 'children'),
    Input('btn-new-data', 'n_clicks'),
    State('current_dataset', 'data'),
    prevent_initial_call=True
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
        class_name="py-1 px-3 mb-0 shadow",
        id={'type': 'label-card', 'index': index, 'label': label},
    )
    return card


@app.callback(
    output={
        "new_label_list": Output('label-list', 'children'),
        "label_button_hide": Output('label-buttons', 'hidden'),
        "dirty_bit": Output('dirty-bit', 'data-labelchanged'),
        "label_input_field": Output('lbl-input', 'value'),
    },
    inputs={
        "triggers": {
            "label_submit": Input('submit-lbl-button', 'n_clicks'),
            "label_enter": Input("lbl-input", "n_submit"),
            "label_remove": Input({'type': 'label-remove-btn', 'index': ALL}, 'n_clicks'),
            "current_dataset": Input('current_dataset', 'data'),
        }
    },
    state={
        "label_input": State('lbl-input', 'value'),
        "children": State('label-list', 'children'),
        "dirty_bit": State('dirty-bit', 'data-labelchanged'),
    },
    prevent_initial_call=True
)
def add_label(triggers, label_input, children, dirty_bit):
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
    if ctx.triggered_id in ['submit-lbl-button', 'lbl-input']:
        if label_input:
            already_there = False
            for label in children[1:]:
                if label_input == label['props']['id']['label']:
                    already_there = True
            if already_there:
                raise PreventUpdate
            else:
                children.append(create_label_card(label_input, len(children)))
    elif ctx.triggered_id == 'current_dataset':
        children = [label_list_header]
        labels = datasets.load_labels(triggers['current_dataset']['project_name'])
        for index, lbl in enumerate(labels):
            children.append(create_label_card(lbl, index))
        return {
            "new_label_list": children,
            "label_button_hide": False,
            "dirty_bit": dirty_bit,
            "label_input_field": ''
        }
    else:
        print(ctx.triggered_id)
        button_id = ctx.triggered_id['index']
        # don't iterate over header
        for child in children[1:]:
            if child['props']['id']['index'] == button_id:
                children.remove(child)
    return {
        "new_label_list": children,
        "label_button_hide": False,
        "dirty_bit": dirty_bit + 1,
        "label_input_field": ''
    }
