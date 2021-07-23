import re
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, ALL


app = dash.Dash(__name__, suppress_callback_exceptions=True)

app.layout = html.Div([
    html.Button("Add Button", id="add-button"),
    html.Button("Crunch the indices", id='cruncher'),
    dcc.Checklist(
        id='checker',
        options=[{'label': 'Auto Crunch Indices', 'value': 'crunch_trigger'},
                 {'label': 'Count up index', 'value': 'running_index'}
                ],
        value=[]
    ),
    html.Ul(id='button-container', children=[]),
])


@app.callback(
    Output('button-container', 'children'),
    Input('add-button', 'n_clicks'),
    Input('cruncher', 'n_clicks'),
    Input({'type': 'remove_button', 'index': ALL}, 'n_clicks'),
    State('button-container', 'children'),
    State('checker', 'value')
)
def display_dropdowns(add_click, crunch_click, remove_click, children, checker ):
    print(dash.callback_context.triggered)
    if add_click:
        trigger_id = dash.callback_context.triggered[0]['prop_id']
        if trigger_id.startswith('add-button'):
            new_button = html.Button(
                f'delete me! number {add_click if "running_index" in checker else len(children)+1}',
                id={
                    'type': 'remove_button',
                    'index': add_click
                },
            )
            children.append(html.Li(new_button))
        elif trigger_id.startswith('cruncher'):
            for new_value, child in enumerate(children, start=1):
                child['props']['children']['props']['children'] = f'delete me! number {new_value}'
        else:
            button_id = int(re.findall('\d+', trigger_id)[0])
            for child in children:
                print(child)
                if child['props']['children']['props']['id']['index'] == button_id:
                    children.remove(child)
        if 'crunch_trigger' in checker:
            for new_value, child in enumerate(children, start=1):
                child['props']['children']['props']['children'] = f'delete me! number {new_value}'
    return children

@app.callback(
    Output('cruncher', 'hidden'),
    Input('checker', 'value')
)
def check_id_cruncher(value):
    return True if 'crunch_trigger' in value else False


if __name__ == '__main__':
    app.run_server(debug=True)
