"""Dash application for annotation of short text usign custom categories and
giving suggestions for similar text units.
"""

import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, MATCH, ALL
from dash_html_components.Button import Button
import datasets
import html_generators
import re
import pandas as pd

app = dash.Dash(__name__)

SIMILARITY_SEARCH_RESULTS = 10



sentences_df, search_index = datasets.dataset_from_csv('sentences')

# get all categories which are set in the csv except 'None' values
categories = [cat for cat in sentences_df['category'].unique() if cat]

app.layout = html.Div([
    html.Div(
        className="app-header",
        children=[
            html.Div('Plotly Dash', className="app-header--title")
        ]
    ),
    html.Div(
        className="arg-list-pane",
        children=[
            html.Div(className="arg-list-box", children=[
                html.Div('Argument Input', className="arg-list-header"),
                dash_table.DataTable(
                    id='arg-table',
                    filter_action="native",
                    columns=[
                        {'name': 'id', 'id': 'id', 'hidden': True},
                        {'name': 'Argument', 'id': 'sentence'},
                        {'name': 'Category', 'id': 'category',  'editable':True, 'presentation': 'dropdown'}
                    ],
                    hidden_columns=[

                    ],
                    dropdown= {
                        'category': {
                            'options': [
                                {'label': cat, 'value': cat} for cat in categories
                            ]
                        }
                    },
                    data=sentences_df[['id', 'sentence','category']].to_dict('records'),
                    style_header={
                        'text_Align': 'center',
                    },
                    style_data={
                        'whiteSpace': 'normal',
                        'height': 'auto',
                        'page_size': '50',
                    },
                    style_data_conditional=[
                        {'if': {'column_id': 'sentence'},
                        'textOverflow': 'ellipsis',
                        'maxWidth': 0,
                        'width': '90%',
                        'textAlign': 'left'
                        #'cursor': 'pointer'
                        }
                    ]
                )]
            ),
            html.Div('Argument Details', id="argument-detail-box")
        ]
    ),
    html.Div(
        className="category-pane",
        children=[
            html.Div(className="category-box", children=[
                html.Div(
                    className="category-header",
                    children=[
                        dcc.Input(id='cat-input', value='Add Category..', type='text'),
                        html.Button(id='submit-cat-button', n_clicks=0, children='Add')
                    ]),
                html.Ul(
                    id='cat_list',
                    children=[
                        html.Div(category, {'type': 'category-item', 'index': index},
                                 className="category-container")
                        for index, category in enumerate(categories)
                    ])
                ]
            ),
            html.Div( id='algo-box', children=[
                html.Div('Similar Arguments', className="algo-box-header"),
                dash_table.DataTable(
                    id='algo-table',
                    columns=[
                        {'name': 'Argument', 'id': 'sentence'},
                        {'name': 'Category', 'id': 'category',  'editable':True, 'presentation': 'dropdown'}
                    ],
                    dropdown= {
                        'category': {
                            'options': [
                                {'label': cat, 'value': cat} for cat in categories
                            ]
                        }
                    },
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
                        {'if': {'column_id': 'sentence'},
                        'textOverflow': 'ellipsis',
                        'maxWidth': 0,
                        'width': '90%',
                        'textAlign': 'left'
                        #'cursor': 'pointer'
                        }
                    ]
                )

            ]
            )
        ]
    )
])


@app.callback(
    Output('cat_list', 'children'),
    Output('arg-table', 'dropdown'),
    Output('algo-table', 'dropdown'),
        Input('submit-cat-button', 'n_clicks'),
        Input("cat-input", "n_submit"),
        Input({'type': 'category-remove-btn', 'index': ALL}, 'n_clicks'),
    State('cat-input', 'value'),
    State('cat_list', 'children'),
    State('arg-table', 'dropdown'),
    State('algo-table', 'dropdown')
)
def add_category(n_clicks, n_submit, remove_click, cat_input, children, arg_dropdown, algo_dropdown):
    """Handle Category input.
    Data from the input box can be submitted with enter and button click. If
    that happens, a new category will be created if it doesn't exist yet.
    If the remove button of a category is presesd, the corresponding list
    element will be deleted.
    """
    if (n_clicks or n_submit) and cat_input:
        trigger_id = dash.callback_context.triggered[0]['prop_id']
        if trigger_id.startswith('submit-cat-button') or trigger_id.startswith('cat-input'):
            already_there = False
            for category in children:
                if cat_input in category['props']['children']:
                    already_there = True
            if not already_there:
                new_cat = html.Li(
                    children=[
                        cat_input,
                        html.Button(
                            'remove',
                            id={'type': 'category-remove-btn', 'index': len(children)})
                    ],
                    id={'type': 'category-item', 'index': len(children)},
                    className="category-container")
                children.append(new_cat)
                arg_dropdown['category']['options'] = arg_dropdown['category']['options'] + [{'label': cat_input, 'value': cat_input}]
                algo_dropdown['category']['options'] = algo_dropdown['category']['options'] + [{'label': cat_input, 'value': cat_input}]
        else:
            button_id = int(re.findall('\d+', trigger_id)[0])
            for child in children:
                if child['props']['children'][1]['props']['id']['index'] == button_id:
                    print(child)
                    children.remove(child)
                    try:
                        arg_dropdown['category']['options'].remove(
                            {'label': child['props']['children'][0], 'value': child['props']['children'][0]
                            })
                    except ValueError:
                        print(f'no option {cat_input} in dropdown')
                    try:
                        algo_dropdown['category']['options'].remove(
                            {'label': child['props']['children'][0], 'value': child['props']['children'][0]
                            })
                    except ValueError:
                        print(f'no option {cat_input} in dropdown')

    return children, arg_dropdown, algo_dropdown


@app.callback(
    Output('argument-detail-box', 'children'),
    Output('arg-table', 'data'),
    Output('algo-table', 'data'),
        Input('arg-table', 'active_cell'),
        Input('arg-table', 'dropdown'),
        Input('arg-table', 'data'),
        Input('algo-table', 'data'),
    State('argument-detail-box', 'children')
)
def handle_input_table_change(active_cell, dropdown, arg_data, algo_data, details_children):
    """handle changes to input table.
    There are two scenarios how the argument details or the data for the algo
    table can change.
    First, another item is clicked. This changes the output of the detail box as
    well as the algorithm output. For the algorithm output, the similarity
    search is conducted and the data of the most similar items is put into the algo-table.
    Second, a category is deleted and the dropdown options change. When this
    happens, the algo-table and the arg-table have to clear the dropdown value
    of all the items that have this category selected.
    Third, a dropdown item is changed in either datatable (algo or arg). If
    that's the case, the change must be reflected in the other table as well.
    """
    if not dash.callback_context.triggered[0]['value']:
        raise dash.exceptions.PreventUpdate
    trigger = dash.callback_context.triggered[0]['prop_id']
    # first case.
    if trigger == 'arg-table.active_cell':
        dff = pd.DataFrame(arg_data)
        sentence_data = sentences_df.iloc[active_cell['row']]
        sentence = sentence_data['sentence']
        details_table = html_generators.create_details_table(sentence_data, header='argument details')
        similarity_indices = datasets.search_faiss_with_string(
            sentence,
            search_index,
            SIMILARITY_SEARCH_RESULTS
        )
        similarity_table_data = dff.iloc[similarity_indices]

        return details_table, arg_data, similarity_table_data.to_dict('records')
    # second case.
    elif trigger == 'arg-table.dropdown':
        # this means that the dropdown changed, second case!
        labels = [cat['label'] for cat in dropdown['category']['options']]
        for index, row in enumerate(arg_data):
            if row['category'] not in labels:
                arg_data[index]['category'] = None
        for index, row in enumerate(algo_data):
            if row['category'] not in labels:
                algo_data[index]['category'] = None
        return details_children, arg_data, algo_data
    # third case, arg-table data has changed.
    elif trigger == 'arg-table.data':
        print (dash.callback_context.triggered)
    elif trigger == 'algo-table.data':
        print (dash.callback_context.triggered)
if __name__ == '__main__':
    app.run_server(debug=True)
