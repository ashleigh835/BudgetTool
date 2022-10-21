from dash import dcc, html
import dash_bootstrap_components as dbc

from app.layouts.common import account_card

tab_Style = {
    'padding': '0',
    'height': '44px',
    'line-height': '44px'
}
page_layout = html.Div(
    [   dcc.Tabs(
            id='tab', 
            value='account management',
            children=[
                dcc.Tab(label='Account Management', value='account management',style=tab_Style,selected_style=tab_Style),
                dcc.Tab(label='User Management', value='user management',style=tab_Style,selected_style=tab_Style),
            ],
        ),
        html.Hr(),
        html.Div(id='tab-content')
    ]
)

def tab_settings_account_management(accounts:dict={}): 
    children = [
        dbc.Row(
            [   dbc.Col(width=5),
                dbc.Col(
                    dbc.Button(
                        'Add Account',
                        id='account-management-add-new', 
                        className='ml-auto w-100 ', 
                        size='sm'
                    ),
                    width=2, 
                    className='justify-content-center mb-3 d-flex',
                    style={'padding-bottom' : '1%'}
                ),
                dbc.Col(width=5),
            ]
        )
    ]
    for account in accounts:
        children += [
            dbc.Row(
                dbc.Col(
                    account_card(account, accounts, True),
                    width={"size":4}
                ),
                justify = "center"
            )
        ]
    return html.Div(children)
