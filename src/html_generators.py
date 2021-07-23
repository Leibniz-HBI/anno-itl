"""Here are all the generated html pieces that are needed.
"""

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash_html_components.Tr import Tr
from dash.dependencies import Input, Output, State, MATCH, ALL
import plotly.express as px


def create_table_row(input_tuple):
    """Create a dash table row from a tuple of inputs
    """
    return html.Tr([html.Td(value) for value in input_tuple])


def create_details_table(sentence_data, header='Details Box View'):
    """Creates a details view for a selected sentence.
    """
    return html.Table(
        className='details-table',
        children= [
            html.Thead(header),
            html.Tbody(
                children= [create_table_row((k,v)) for k,v in  sentence_data.items()]
            )
        ]
    )


