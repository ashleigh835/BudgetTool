import dash_bootstrap_components as dbc
from dash import dcc, html 

from app.transaction import Transaction

def nav_bar(dash) -> html:
    nav_drop_down = dbc.DropdownMenu(
        [   dbc.DropdownMenuItem("Home", href="/Home"),
            dbc.DropdownMenuItem("Transactions", href="/Transactions"),
            dbc.DropdownMenuItem("Budgeting", href="/Budgeting"),
            dbc.DropdownMenuItem(divider=True),
            dbc.DropdownMenuItem("Settings", href="/Settings"),
        ],
        label="Menu",
        id="menu_drop_down",
        align_end=True
    )
    return dbc.Navbar(
        [   dbc.Container(
                [   html.A(
                        dbc.Row(
                            [   dbc.Col(
                                    [   html.Img(src=dash.get_asset_url('IconW.png'), height='50px', style={'padding-left':'1%','padding-top':'0%','padding-bottom':'0%'}),
                                        dbc.NavbarBrand("Budget Tool",className="ms-2", style={'font-size': 30, 'padding-left':'1%', 'text-align':'left'})
                                    ],
                                    width=9
                                ),
                                dbc.Col(
                                    dcc.Markdown("""Icons made by [Eucalyp](https://www.flaticon.com/authors/eucalyp) from [Flaticon](https://www.flaticon.com/)""",
                                    style = {'font-size': 10, 'text-align':'right', 'color':'white','padding-left':'0%'}),
                                    width=2
                                )
                            ],
                            align='center'
                        ),
                        style={"width":"100%"}
                    ),
                    nav_drop_down
                ],
                fluid=True,
            )
        ],
        color = 'dark',
        dark=True
    )

def account_creation_modal(gui, is_open:bool=False) -> html:
    if len(gui._A_M._users)==0:
        select_holder = dbc.FormFloating(
            [   dbc.Input(type="text", id='account_holder', valid=False),
                dbc.Label("Account Holder"),
                dbc.FormText("Enter the name of the person who holds this account",color="secondary",),
                
            ],
            className="mb-3"
        )
    else:
        select_holder = dbc.Row(
            [   dbc.Label("Account Holder", html_for="account_holder", width=4),
                dbc.Col(
                    dbc.RadioItems(
                        id="account_holder",
                        options = [{"label": holder, "value": holder} for holder in gui._A_M._users],
                        value=gui._A_M._users[0]
                    ),
                    width=8,
                ),
            ],
            className="mb-3",
            )
    return dbc.Modal(
        [   dbc.ModalHeader("Initial Account Set-Up"),
            dbc.Card(
                [   dbc.FormFloating(
                        [   dbc.Input(type="text", id='account_name'),
                            dbc.Label("Account Nickname"),
                            dbc.FormText("Enter a nickname for your account",color="secondary",),
                            dbc.FormFeedback(id='account_name_feedback', type="invalid")
                        ],
                        className="mb-3"
                    ),
                    select_holder,
                    dbc.Row(
                        [   dbc.Label("Account Type", html_for="account_type", width=4),
                            dbc.Col(
                                dbc.RadioItems(
                                    id="account_type",
                                    options = [{"label": account_type, "value": account_type} for account_type in gui.settings['account_types']],
                                    value=gui.settings['account_types'][0]
                                ),
                                width=8,
                            ),
                        ],
                        className="mb-3",
                    ),
                    dbc.Row(
                        [   dbc.Label("Account Provider", html_for="account_provider", width=4),
                            dbc.Col(
                                dbc.RadioItems(
                                    id="account_provider",
                                    options = [{"label": account_provider, "value": account_provider} for account_provider in Transaction._supported_providers],
                                    value=Transaction._supported_providers[0]
                                ),
                                width=8,
                            ),
                        ],
                        className="mb-3",
                    )
                ],
                style={ 'padding':'2%'}
            ),
            dbc.ModalFooter(
                [   dbc.Button("Add New Account", id='create-account', className="ml-auto",color='success', size="sm"),
                ]
            ),
        ],
        id="first-time-set-up-modal",
        size="md",
        centered=True,
        is_open=is_open,
    )

def account_card(selected_account_nickname:str, data:dict, manage:bool=False) -> list:
    header = dbc.CardHeader([html.H5(selected_account_nickname)])
    footer = ""
    children_sm = []
    children_big = []
    for info in data[selected_account_nickname].keys():
        if info == 'Account Holder':
            footer = dbc.CardFooter(html.Small(f"{data[selected_account_nickname][info]}", className="card-text text-muted"))
        elif info in (['Type','Provider']):
            children_sm+=[html.Div(html.Small(f"{info}: {data[selected_account_nickname][info]}", className="card-text text-muted"))]
        else:
            children_big+=[html.Div(f"{info}: {data[selected_account_nickname][info]}", className="card-text")]

    style = {}
    if not manage:
        style = {'display':'none'}
        
    return [
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    [   header,
                        dbc.CardBody(children_big + [html.Div(style={'padding':'1%'})] + children_sm),
                        footer,
                        dbc.Badge(
                            "manage",
                            color="info",
                            pill=True,
                            className="me-1 text-decoration-none position-absolute top-0 start-50 translate-middle",
                            href='#',
                            n_clicks = 0,
                            id={'type':f'manage_a','index':selected_account_nickname},
                            style=style
                        )
                    ],
                    className='mb-3', # w-50',
                    # style = {"height": "25vh"}
                ),
            ),
            justify = "center", align = 'center'
        )
    ]