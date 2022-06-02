"""Everything that displays data from the backend
"""

from dash import html
import dash_bootstrap_components as dbc
import numpy as np


def create_label_pill(label, id):
    pill = dbc.Badge([
        label,
        dbc.Button(
            className="bi bi-x py-0 px-1 position-absolute end-0 border-0 badge rounded-pill",
            id={'type': 'tu-label-remove-btn', 'index': id, 'label': label},
            style={'color': 'white', 'height': '100%', 'background': 'red'},
        )],
        pill=True, color="primary", className="me-1",
        id={'type': 'tu-label-pill', 'index': id, 'label': label}
    )
    return pill


def create_data_card(text_unit, labels, label_key, text_key):
    """Creates a data display container, which is a bootstrap card.
    The index is important for pattern matching callbacks. It is not only put on
    the button but also on the card itself, so that check for the index is not
    so long. (so you can use ['props']['id']['index'] instead of going down to
    the button.)
    The label is part of the `id` dict for a similar reason

    Args:
        label_name: name of the label key
        text_unit: dictionary with text unit information.
        index: position of the card in the list of cards.

    Returns:
        [type]: dbc.Card with the stuff needed.
    """
    card = dbc.Card([
        dbc.CardBody([
            dbc.Row(
                dbc.Col(
                    id={'type': 'data-btn-container', 'index': text_unit['id']},
                    className=" mb-3 bg-secondary",
                    children=[
                        dbc.Button(
                            html.Span([html.I(className="bi bi-tag py-0 px-1"), "Add Label"]),
                            id={'type': 'tu-open-label-collapse', 'index': text_unit['id']}
                        ),
                        dbc.Button(
                            html.Span([html.I(className="bi bi-arrow-left-right py-0 px-1"), "Get similar text"]),
                            id={'type': 'tu-similarity-search', 'index': text_unit['id']}
                        ),
                        dbc.Collapse([
                            dbc.Card(
                                dbc.Row([
                                    dbc.Col(
                                        dbc.RadioItems(
                                            options=[
                                                {"label": label, "value": label}
                                                for label in labels
                                            ],
                                            id={'type': 'add-label-radio-input', 'index': text_unit['id']},
                                            value=text_unit[label_key]
                                            if text_unit[label_key] and not np.isnan(text_unit[label_key])
                                            else None
                                        )
                                    ),
                                    dbc.Col(
                                        dbc.Button(
                                            html.Span([html.I(className="bi bi-plus-square"), "add"]),
                                            id={'type': 'tu-submit-lbl-btn', 'index': text_unit['id']}
                                        )
                                    )
                                ]),
                            )],
                            id={'type': 'add-lbl-collapse', 'index': text_unit['id']},
                            is_open=False,
                        )
                    ]
                )
            ),
            dbc.Row(
                dbc.Col(
                    html.P(
                        text_unit[text_key],
                        id={'type': 'text-unit', 'index': text_unit['id']}
                    )
                )
            )
        ]),
        dbc.CardFooter(
            create_label_pill(text_unit[label_key], text_unit['id'])
            if text_unit[label_key] and not np.isnan(text_unit[label_key])
            else 'add_label',
            id={'type': 'tu-footer', 'index': text_unit['id']},
        ),
    ],
        class_name="py-1 px-3 mb-0 shadow",
        id={'type': 'tu-card', 'index': text_unit['id']},
    )
    return card
