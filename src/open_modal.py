from dash import dcc
import dash.html as html
import dash_bootstrap_components as dbc
import datasets


dataset_name_input = html.Div([
    dbc.Input(placeholder="Dataset Name", type="text", id='ds-name-input'),
    dbc.FormText("Please only _, A-Z,a-z and numbers; between 4 and 30 characters"),
    dbc.FormFeedback(
        "Dataset name is valid and not taken", type="valid"
    ),
    dbc.FormFeedback(
        "This name is not okay (never displayed, I think)",
        id='dataset-name-invalid-message',
        type="invalid",
    )
])


dataset_upload = html.Div([
    dcc.Upload(
        dbc.Button([dbc.Spinner(html.Div('Upload Dataset',
                    id="dataset-load-spinner"), size="sm")],
                   color="primary",
                   id='dataset-upload-button'
                   ),
        id='dataset-file-input',
    ),
    dbc.FormText("must be a .csv, .tsv or .xls file")
])

text_unit_dropdown = dbc.Select(
    id='ds-text-unit-dd',
    placeholder="Select a dataset column as text units (after upload)",
    disabled=True
)


dataset_description_input = html.Div([
    dbc.Textarea(placeholder='Dataset description', id='ds-description-input'),
    dbc.FormText("""short description of the dataset,
     min 10, max 500 characters, no special chars please or I will personally come to your door"""),
    dbc.FormFeedback(
        "Description is valid, at least formally.", type="valid"
    ),
    dbc.FormFeedback(
        "This name is not okay (never displayed, I think)",
        id='dataset-description-invalid-message',
        type="invalid",
    )
])


dataset_submit_button = html.Div([
    dbc.Button(
        dbc.Spinner(html.Div('Add Dataset!', id="dataset-create-spinner"), size="sm"),
        color="success",
        id='add-dataset-btn'
    ),
    dbc.FormText("create dataset", id='submit-text')
])


create_dataset_form = dbc.Form([dataset_name_input,
                               dataset_upload,
                               text_unit_dropdown,
                               dataset_description_input,
                               dataset_submit_button],
                               style={'width': '55%', 'display': 'inline-block'},
                               className="gy-5")


def create_project_name_input(id, enabler=True):
    return html.Div([
        dbc.Input(placeholder="Project Name", type="text", id=id, disabled=not enabler),
        dbc.FormText("Please only _, A-Z,a-z and numbers; between 4 and 30 characters"),
        dbc.FormFeedback(
            "Project name is valid and not taken", type="valid"
        ),
        dbc.FormFeedback(
            "This name is not okay (never displayed, I think)",
            id=f'{id}-invalid-message',
            type="invalid",
        )
    ])


check_project = dbc.Checkbox(
    id="ds-project-checkbox",
    className="checkbox-form",
    value=True,
    label="Create Project from Dataset?",
    label_class_name='checkbox-form-label'
)


check_label_input = dbc.Checkbox(
    id="ds-project-label-checkbox",
    className="checkbox-form",
    value=True,
    label="Add label information from dataset?",
    label_class_name='checkbox-form-label'
)


label_selection_dropdown = dbc.Select(
    id='ds-project-label-selection-dd',
    placeholder="Select a dataset column as label information (after upload)",
    disabled=True)


create_project_form = dbc.Form([
    check_project,
    create_project_name_input('new-ds-proj-name'),
    check_label_input, label_selection_dropdown],
    style={'width': '40%', 'display': 'inline-block', 'float': 'right'},
    className="gy-5"
)


def create_open_dropdown_options(existing_projects, current_project):
    options = []
    for project in existing_projects:
        if project == current_project:
            options.append({
                'label': f'{project} (currently open)',
                'value': project, 'disabled': True
            })
        else:
            options.append({'label': project, 'value': project})
    return options


def open_project_modal(current_project):

    existing_projects = datasets.load_meta_file('projects_meta.yaml')
    existing_datasets = datasets.load_meta_file('datasets_meta.yaml')

    open_error = html.Div(
        [html.Span(
            'No Projects were created yet. Create one from an existing Dataset or Add A Dataset',
            className='warning'),
         html.Br()],
        hidden=True if existing_projects else False
    )
    open_dropdown = dbc.Select(
        id='open-project-dd',
        options=create_open_dropdown_options(existing_projects, current_project),
        placeholder="Select a project to open",
        disabled=not existing_projects
    )
    open_button = dbc.Button(
        "Open Project", color="success", id='open-project-btn', disabled=not existing_projects
    )
    open_form = dbc.Form(
        [open_error, open_dropdown, open_button],
        style={'width': '45%', 'float': 'left'}
    )

    create_error = html.Div([
        html.Span(
            'No Datasets available on the Server! Create a new Dataset first',
            className='warning'),
        html.Br()],
        hidden=True if existing_projects else False
    )
    create_dropdown = dbc.Select(
        id='create-project-dd',
        options=[{'label': dataset, 'value': dataset} for dataset in existing_datasets],
        placeholder="Select a Dataset for project creation",
        disabled=not existing_datasets
    )

    create_label_input = dbc.Checkbox(
        id="create-project-label-checkbox",
        className="checkbox-form",
        value=True,
        label="Add label information from dataset?",
        label_class_name='checkbox-form-label'
    )

    create_label_selection_dropdown = dbc.Select(
        id='create-project-label-selection-dd',
        placeholder="Select a dataset column as label information",
        disabled=True
    )

    create_button = html.Div([
        dbc.Button(
            "Create Project", color="success", id='create-project-btn',
            disabled=not existing_datasets
        ),
        dbc.FormText("Create Project", id='proj-create-text')]
    )
    create_form = dbc.Form([
        create_error, create_dropdown,
        create_project_name_input('create-proj-name', existing_datasets),
        create_label_input, create_label_selection_dropdown, create_button],
        style={'width': '45%', 'float': 'left'})

    modal = dbc.Modal([
        dbc.ModalHeader("Open or create a new project"),
        dbc.ModalBody(
            dbc.Tabs([
                dbc.Tab(
                    dbc.Card(
                        dbc.CardBody([
                            html.H4(
                                "Open",
                                className="card-title",
                                style={'width': '45%', 'float': 'left'}),
                            html.H4(
                                "Or create from dataset",
                                className="card-title",
                                style={'width': '45%', 'float': 'right'}),
                            open_form,
                            create_form,
                            html.Div(
                                hidden=True,
                                id='create-validator',
                                **{'data-create-valid': False})
                        ]),
                    ),
                    label="Open or Create Project"
                ),
                dbc.Tab(
                    dbc.Card(
                        dbc.CardBody([
                            html.H4("Add new Dataset", className="card-title"),
                            create_dataset_form,
                            create_project_form,
                            html.Div(
                                hidden=True,
                                id='add-validator',
                                **{'data-upload-valid': False})
                        ]),
                    ),
                    label="Add New Dataset"
                )
            ])
        ),
        dbc.ModalFooter(
            dbc.Button(
                "Close", id="close-upload-btn", n_clicks=0
            )
        )
    ],
        id="manage-datasets-modal",
        size="xl",
        is_open=True,
    )
    return modal
