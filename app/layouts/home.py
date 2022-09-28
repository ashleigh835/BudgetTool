from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc

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
        header = dbc.CardHeader([html.H5(account)])
        footer = ""
        great_children_sm = []
        great_children_big = []
        for info in accounts[account].keys():
            if info == 'Account Holder':
                footer = dbc.CardFooter(html.Small(f"{accounts[account][info]}", className="card-text text-muted"))
            elif info in (['Type','Provider']):
                great_children_sm+=[html.Div(html.Small(f"{info}: {accounts[account][info]}", className="card-text text-muted"))]
            else:
                great_children_big+=[html.Div(f"{info}: {accounts[account][info]}", className="card-text")]
        
        great_children = great_children_big + [html.Div(style={'padding':'1%'})] + great_children_sm
        children += [
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        [   header,
                            dbc.CardBody(great_children),
                            footer
                        ],
                        className='mb-3 w-50',
                    ),
                    width={"size":8,'offset':4}
                ),
                justify = "center"
            )
        ]
    return html.Div(children)
