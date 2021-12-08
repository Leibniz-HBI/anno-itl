"""Here are all the generated html pieces that are needed.
"""

import dash.html as html


def create_table_row(input_tuple):
    """Create a dash table row from a tuple of inputs
    """
    return html.Tr([html.Td(value) for value in input_tuple])


def create_details_table(sentence_data, header='Details Box View'):
    """Creates a details view for a selected sentence.
    """
    return html.Table(
        className='details-table',
        children=[
            html.Thead(header),
            html.Tbody(
                children=[create_table_row((k, v)) for k, v in sentence_data.items()]
            )
        ]
    )
