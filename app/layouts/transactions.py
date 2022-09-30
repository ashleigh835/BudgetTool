from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px

from app.account import Account

tab_Style = {
    'padding': '0',
    'height': '44px',
    'line-height': '44px'
}

page_layout = html.Div(
    [   dcc.Tabs(
            id='tab', 
            value='transactions', 
            children=[
                dcc.Tab(label='Transactions', value='transactions',style=tab_Style,selected_style=tab_Style),
                dcc.Tab(label='Scheduled Transactions', value='sched transactions',style=tab_Style,selected_style=tab_Style),
            ],
        ),
        html.Hr(),
        html.Div(id='tab-content')
    ]
)

upload_transactions_box = dcc.Upload(
    id='upload-transactions',
    children=['Drag and Drop or click to upload Transactions'], 
    style={
        'width': '100%',
        "height": "25vh",
        # 'height': '100%',#style={"height":"100%"} or with bootstrap: className="h-100" then the graph will fill the parent container.
        'lineHeight': '60px',
        'borderWidth': '1px',
        'borderStyle': 'dashed',
        'borderRadius': '5px',
        'textAlign': 'center'
    },
)

def tab_transactions_summary(accounts:dict={}):
    return html.Div(
        [   dbc.Row(
                [   dbc.Col(width=3),
                    dbc.Col(
                        dcc.Dropdown([account for account in accounts.keys()], list(accounts.keys())[0], id='transaction-selected-account-dropdown'),
                        className='mb-3',
                        width=6
                    ),
                    dbc.Col(width=3),
                ],
                className='mb-3',
                style = {'padding-left':'1%','padding-right':'1%'}                
            ),
            dbc.Row(
                [   dbc.Col(
                        upload_transactions_box, 
                        width=3,
                    ),
                    dbc.Col('temp', id='transaction-selected-account-detail', width=6),
                    dbc.Col(width=3)
                ],
                className='mb-3',
                style = {'padding-left':'1%','padding-right':'1%'}           
            ),
            dbc.Row(
                [   dbc.Col(
                        dbc.Card(
                            'test',
                            id='transaction-graph', # dcc.Graph(id='example-graph', figure=fig),
                            # className='mb-3'
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
                style={'padding-left':'1%','padding-right':'1%','padding-bottom':'1%'}
            ),
            dbc.Row(
                id = 'transaction-data',
                style = {'padding-left':'1%','padding-right':'1%','padding-bottom':'1%'}
            )
        ]
    )

def account_visuals(selected_account:Account) -> tuple:
    if selected_account._T_M._df.empty:
        graph = 'No Transactions'
        dta = 'No Transactions'
    else:
        df = selected_account._T_M._df.copy()[['amount','type','date','description','payment_type','balance']]
        df['date'] = df.date.dt.date
        df['amount'] = df.amount.astype('float64')        
        ax = df.groupby('date', as_index=False).agg({'balance':'last'})
        fig = px.area(ax, x = 'date',y = 'balance')#, color="City", barmode="group")
        graph = dcc.Graph(id='example-graph', figure=fig, className='mb-3')              
        dta = dash_table.DataTable(
            data=df.to_dict('records'), 
            columns=[{"name": i, "id": i} for i in df.columns],
            style_data={
                # 'whiteSpace': 'normal',
                # 'height': 'auto',
                # 'lineHeight': '15px',
                'overflow': 'hidden',
                'textOverflow': 'ellipsis',
                'maxWidth': 0,
            },
            style_cell_conditional=[
                {'if': {'column_id': 'description'},
                    'width': '40%',
                    'textOverflow': 'ellipsis'},
            ],
            tooltip_data=[
                {   column: {'value': str(value), 'type': 'markdown'}
                    for column, value in row.items()
                } for row in df.to_dict('records')
            ],
            tooltip_duration=None
        )
    return graph, dta