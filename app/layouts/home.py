from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc

from app.layouts.common import account_card

tab_Style = {
    'padding': '0',
    'height': '44px',
    'line-height': '44px'
}

page_layout = html.Div(
    [   #dcc.Store(id='overview-df', storage_type='session',clear_data=True),
        dcc.Tabs(
            id='tab', 
            value='overview', 
            children=[
                dcc.Tab(label='Overview', value='overview',style=tab_Style,selected_style=tab_Style),
                dcc.Tab(label='Accounts', value='accounts',style=tab_Style,selected_style=tab_Style),
            ],
        ),
        html.Hr(),
        html.Div(id='tab-content')
    ]
)

def tab_overview(df, fig):
    return html.Div(
        [   dbc.Row(
                [   dbc.Col(
                        dbc.Card(
                            dcc.Graph(id='example-graph', figure=fig),
                            className='mb-3',
                        ),
                        width=8
                    ),
                    dbc.Col(
                        dbc.Row(
                            [dbc.Card('test',className='mb-3'),dbc.Card('test',className='mb-3')]
                        ),
                        width=4
                    )
                ],
                style={'padding-left':'1%','padding-right':'1%'}
            ),
            dbc.Row(
                [   dash_table.DataTable(df.to_dict('records'), [{"name": i, "id": i} for i in df.columns])],
                style={'padding-left':'1%','padding-right':'1%'}
            )
        ]
    )

def tab_accounts(accounts:dict={}): 
    children = []
    for account in accounts:
        children += [
            dbc.Row(
                dbc.Col(
                    account_card(account, accounts),
                    width={"size":4}
                ),
                justify = "center"
            )
        ]
    return html.Div(children)
