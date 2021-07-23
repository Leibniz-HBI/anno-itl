import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, MATCH, ALL
from dash_html_components.Button import Button
import datasets
import html_generators
import re

app = dash.Dash(__name__)


sentences, embeddings = datasets.dataset_from_csv('sentences')
categories = set(sentence['category'] for sentence in sentences if sentence['category'])




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
                html.Div('Header', className="arg-list-header"),
                html.Ul(children=[
                    html.Div(
                        sentence['sentence'],
                        id={'type': 'argument-container', 'index': sentence['id']},
                        className="arg-container") for sentence in sentences]
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
            html.Div("algorithm output here", id='algo-box')
        ]
    )
])


@app.callback(
    Output('cat_list', 'children'),
              Input('submit-cat-button', 'n_clicks'),
              Input("cat-input", "n_submit"),
              Input({'type': 'category-remove-btn', 'index': ALL}, 'n_clicks'),
              State('cat-input', 'value'),
              State('cat_list', 'children')
)
def add_category(n_clicks, n_submit, remove_click, cat_input, children):
    """Handle Category input.
    Data from the input box can be submitted with enter and button click. If
    that happens, a new category will be created if it doesn't exist yet.
    If the remove button of a category is presesd, the corresponding list
    element will be deleted.
    """
    if n_clicks or n_submit:
        trigger_id = dash.callback_context.triggered[0]['prop_id']
        if trigger_id.startswith('submit-cat-button') or trigger_id.startswith('cat-input'):
            already_there = False
            for category in children:
                if cat_input in category['props']['children']:
                    already_there = True
            if not already_there:
                new_cat = html.Li(
                    children= [
                        cat_input,
                        html.Button(
                            'remove',
                            id={'type': 'category-remove-btn', 'index': len(children)})
                    ],
                    id={'type': 'category-item', 'index': len(children)},
                    className="category-container")
                children.append(new_cat)
        else:
            button_id = int(re.findall('\d+', trigger_id)[0])
            for child in children:
                if child['props']['children'][1]['props']['id']['index'] == button_id:
                    children.remove(child)
    return children


@app.callback(
    Output('argument-detail-box', 'children'),
    Output('algo-box', 'children'),
    Input({'type': 'argument-container', 'index': ALL}, 'n_clicks')
)
def handle_arg_click(n_clicks):
    """handle click on a list item.
    When a list item is clicked, the n_clicks property will update, the callback
    will be triggered and the responsible list element will be stored in
    `dash.callable_context.triggered`. From that, the index/id of the sentence
    is known. With that information, the algorithm can be fed and the info box
    can be changed.
    """
    if not dash.callback_context.triggered[0]['value']:
        raise dash.exceptions.PreventUpdate


    sentence_id = int(re.findall('(\d+)',dash.callback_context.triggered[0]['prop_id'])[0])
    print(dash.callback_context.triggered)


    sentence_data = sentences[sentence_id]
    details_table = html_generators.create_details_table(sentence_data, header='argument details')
    return details_table, 'Similarity Score list here'




if __name__ == '__main__':
    app.run_server(debug=True)
