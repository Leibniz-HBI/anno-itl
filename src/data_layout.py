"""Everything that displays data from the backend
"""

from dash import html
import dash_bootstrap_components as dbc


def create_label_pill(label, id):
    pill = dbc.Badge([
        "label",
        dbc.Button(
            className="bi bi-x py-0 px-1 position-absolute end-0 border-0",
            id={'type': 'tu-label-remove-btn', 'index': id, 'label': label},
            style={'color': 'white', 'height': '100%', 'background': 'red'},
        )],
        pill=True, color="primary", className="me-1",
        id={'type': 'tu-label-pill', 'index': id, 'label': label}
    )
    return pill


def create_data_card(project_name, text_unit, labels):
    """Creates a data display container, which is a bootstrap card.
    The index is important for pattern matching callbacks. It is not only put on
    the button but also on the card itselve, so that check for the index is not
    so long. (so you can use ['props']['id']['index'] instead of going down to
    the button.)
    The label is part of the `id` dict for a similar reason

    Args:
        text_unit: dictionary with text unit information.
        index: position of the card in the list of cards.

    Returns:
        [type]: dbc.Card with the stuff needed.
    """
    card = dbc.Card([
        dbc.CardHeader([
            html.H6(f"ID: {text_unit['id']}", className='card-title'),
            html.Div(
                id={'type': 'data-btn-container', 'index': text_unit['id']},
                className="position-absolute top-0 end-0 border-0",
                children=[
                    dbc.DropdownMenu([
                        dbc.DropdownMenuItem(
                            label, id={
                                'type': 'tu-add-label-dd-item',
                                'index': text_unit['id'],
                                'label': label},
                            n_clicks=0
                        )
                        for label in labels],
                        className="bi bi-x py-0 px-1 position-absolute top-0 end-0 border-0",
                        id={'type': 'tu-add-label-dd', 'index': text_unit['id']},
                        style={'color': 'white', 'height': '100%', 'background': 'red'},
                    ),
                ])
        ]),
        dbc.CardBody(text_unit['text']),
        dbc.CardFooter(
            create_label_pill(text_unit[f'{project_name}_label'], text_unit['id'])
            if text_unit[f'{project_name}_label']
            else 'add_label'
        ),
    ],
        class_name="py-1 px-3 mb-0 shadow",
        id={'type': 'tu-card', 'index': text_unit['id']},
    )
    return card
