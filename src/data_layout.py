"""Everything that displays data from the backend
"""

from dash import html
import dash_bootstrap_components as dbc
import numpy as np


def create_label_pill(label, id):
    pill = dbc.Badge(
        label,
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
                    className=" mb-3 border-bottom border-1",
                    children=[
                        dbc.Button(
                            html.Span([html.I(className="bi bi-tag py-0 px-1"), "Add Label"]),
                            id={'type': 'tu-open-label-collapse', 'index': text_unit['id']}
                        ),
                        dbc.Button(
                            html.Span([html.I(className="bi bi-arrow-left-right py-0 px-1"), "Get similar text"]),
                            id={'type': 'tu-similarity-search', 'index': text_unit['id']}
                        ),
                        dbc.Collapse(
                            html.Div([
                                dbc.RadioItems(
                                    options=[
                                        {"label": label, "value": label}
                                        for label in labels
                                    ],
                                    id={'type': 'tu-label-select', 'index': text_unit['id']},
                                    value=text_unit[label_key]
                                    if text_unit[label_key] and not np.isnan(text_unit[label_key])
                                    else None,
                                    inline=True
                                )],
                                className="my-2"
                            ),
                            id={'type': 'add-lbl-collapse', 'index': text_unit['id']},
                            is_open=False,
                        )
                    ]
                )
            ),
            dbc.Row(
                dbc.Col(
                    html.H4(
                        text_unit[text_key],
                        id={'type': 'text-unit', 'index': text_unit['id']}
                    )
                )
            )
        ]),
        dbc.CardFooter(
            create_label_pill(text_unit[label_key], text_unit['id'])
            if text_unit[label_key] and not np.isnan(text_unit[label_key])
            else 'Add a label to the Text and see its label set here!',
            id={'type': 'tu-footer', 'index': text_unit['id']},
        ),
    ],
        class_name="py-1 px-3 mb-0 shadow",
        id={'type': 'tu-card', 'index': text_unit['id']},
    )
    return card
