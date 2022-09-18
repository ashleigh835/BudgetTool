from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State

tab_Style = {
    'padding': '0',
    'height': '44px',
    'line-height': '44px'
}

page_layout = html.Div(
    [   #dcc.Store(id='overview-df', storage_type='session',clear_data=True),
        dcc.Tabs(
            id='db-tab', 
            value='overview', 
            children=[
                dcc.Tab(label='Overview', value='overview',style=tab_Style,selected_style=tab_Style),
                dcc.Tab(label='Accounts', value='accounts',style=tab_Style,selected_style=tab_Style),
            ],
        ),
        html.Hr(),
        html.Div(id='db-tab-content')
    ]
)

def tab_overview(df, fig):
    return html.Div(
    [   dcc.Graph(id='example-graph', figure=fig),
        dash_table.DataTable(df.to_dict('records'), [{"name": i, "id": i} for i in df.columns])
    ]
)

def tab_accounts(): 
    return html.Div("test")