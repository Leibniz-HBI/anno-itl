"""Callbacks for opening new projects
"""
import re
from app import app
import dash
from dash.dependencies import Input, Output, State

import datasets


@app.callback(
    Output('dataset-name-invalid-message', 'children'),
    Output('ds-name-input', 'valid'),
    Output('ds-name-input', 'invalid'),
    Input('ds-name-input', 'value')
)
def validate_dataset_name_creation(name):
    """checks whether the name for a dataset is valid and not taken"""

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
    """checks whether the description for a dataset is valid"""

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
    """checks whether the uploaded file is valid"""

    if not dash.callback_context.triggered[0]['value']:
        raise dash.exceptions.PreventUpdate
    valid_file_endings = ['.xls', '.csv', '.ctv']
    if not filename[-4:] in valid_file_endings:
        return 'danger', 'Not a valid File type', {}, True, [], []
    df = datasets.parse_contents(upload, filename)
    if df is not None:
        options = [{'label': key, 'value': key} for key in df.keys()]
        label_options = [{
            'label': f'{key} ({df[key].nunique()} unique items)',
            'value': key}
            for key in df.keys()]
        return 'success', 'Dataset valid', df.to_dict('records'), False, options, label_options
    else:
        return 'danger', 'File was not readable', {}, True, [], []


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
def validate_add_dataset(
        n_clicks, name_valid, desc_valid, new_data,
        project_name_checked, project_name_valid,
        text_unit_selection, proj_label_selection, label_checked):
    if not dash.callback_context.triggered[0]['value']:
        """validates the input for adding a new dataset and creates the error
        message when something is missing."""
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
def validate_create_project(n_clicks, name_valid, label_checked, label_selection, proj_selection):
    """validates all inputs for the creation of a new project and displays error
    message if something is missing or not valid."""
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
    """checks whether a project name for a new project is valid and not taken"""
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
    Output('new-ds-proj-name-invalid-message', 'children'),
    Output('new-ds-proj-name', 'valid'),
    Output('new-ds-proj-name', 'invalid'),
    Input('new-ds-proj-name', 'value')
)
def validate_ds_project_name(name):
    """checks, whether a project name from a new dataset is valid and not taken"""
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
    Output('create-project-label-selection-dd', 'options'),
    Input('create-project-dd', 'value')
)
def get_label_options(dataset):
    """populates dropdown for labels to pick from dataset as labels for new project"""
    if not dash.callback_context.triggered[0]['value']:
        raise dash.exceptions.PreventUpdate

    columns = datasets.get_dataset_labels(dataset)
    return [{'label': f'{key[0]} ({key[1]} unique items)', 'value': key[0]} for key in columns]


@app.callback(
    Output('ds-project-label-selection-dd', 'disabled'),
    Input('ds-project-label-checkbox', 'value'),
    Input('ds-project-label-selection-dd', 'options')
)
def add_label_enabler(checked, options):
    """enables label selection, if the checkbox is checked and a dataset was uploaded"""
    if options and checked:
        return False
    else:
        return True


@app.callback(
    Output('create-project-label-selection-dd', 'disabled'),
    Input('create-project-label-checkbox', 'value'),
    Input('create-project-label-selection-dd', 'options')
)
def create_label_enabler(checked, options):
    """enables label selection, if checkbox is checked and a data was chosen for
    project creation"""
    if options and checked:
        return False
    else:
        return True


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
        create_proj_dd_selection, create_project_name, create_project_name_valid,
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
        return add_dataset_cb(
            new_data, ds_project_name_checked,
            ds_name, ds_text_unit_selection, ds_label_selection if label_checked else False,
            ds_description, ds_project_name, current_dataset
        )
    elif trigger == 'create-validator':
        return create_project_cb(
            create_project_name_valid, create_proj_dd_selection,
            create_project_name, current_dataset,
            create_proj_label_selection if create_label_checked else False
        )
    elif trigger == 'open-project-btn':
        if open_project_dd_selection:
            return open_project_cb(open_project_dd_selection)
        else:
            return True, current_dataset


def create_project_cb(
        create_project_name_valid, create_proj_dd_selection,
        create_project_name, current_dataset, label_column):
    """callback for the create Project Button.

    Args:
        create_project_name_valid: whether the new project name is valid
        create_proj_dd_selection: selected dataset for project creation
        create_project_name: name for new project
        current_dataset: currently loaded datasets
        n_dataset_loads: number of datasets loads so far

    Returns:
        The info about whether the Modal should
        be closed and the updated current dataset
    """
    if create_project_name_valid and create_proj_dd_selection:
        new_current_project = datasets.create_project(
            create_proj_dd_selection,
            create_project_name,
            label_column
        )
        return False, {
            'dataset_name': create_proj_dd_selection,
            'project_name': create_project_name,
            'data': new_current_project.to_dict('records')
        }
    else:
        return True, current_dataset


def open_project_cb(open_project_dd_selection):
    """Callback for the Open project button.

    needs just the project that has to be opened

    Args:
        open_project_dd_selection: project to open (from dropdown)

    Returns:
        The info about whether the Modal should
        be closed and the updated current dataset
    """
    new_current_project, dataset_name = datasets.load_project(open_project_dd_selection)
    return False, {
        'dataset_name': dataset_name,
        'project_name': open_project_dd_selection,
        'data': new_current_project.to_dict('records')
    }


def add_dataset_cb(
        new_data, project_name_checked, dataset_name,
        text_column, label_column, description,
        project_name, current_dataset):
    """Callback for the add dataset button.

    The function assumes everything to be valid, since it can only be trigger if
    the validator is true.
    """
    datasets.create_dataset(new_data, dataset_name, description, text_column)
    if project_name_checked:
        new_current_project = datasets.create_project(dataset_name, project_name, label_column)
        return False, {
            'dataset_name': dataset_name,
            'project_name': project_name,
            'data': new_current_project.to_dict('records')
        }
    else:
        return False, current_dataset
