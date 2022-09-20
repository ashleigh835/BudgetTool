from app.common.config_info import Config
from app.account import Account_Manager
from app.transaction import Transaction

from app.layouts.home import page_layout as h_page, tab_overview, tab_accounts

import dash_bootstrap_components as dbc
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate


import plotly.express as px
import json
import os

class App(object):
    def __init__(self) -> None:
        self.settings = Config().settings()
        self._account_config_path = self.settings['account_config']
        self._account_config = self._determine_config()
        self._A_M = self._load_accounts()

        self.dash = self._initialize()
        self.dash.title = 'Budget Tool'
        self._get_layouts()

        if self.dash is not None and hasattr(self, 'callbacks'):
            self.callbacks(self.dash)
            
        self._run()


        # if self._check_save(): self._save()
        pass

    def __setattr__(self, __name, __value) -> None:
        self.__dict__[__name] = __value
        pass
        
    def _initialize(self) -> object:
        return dash.Dash(__name__, 
            external_stylesheets=[dbc.themes.BOOTSTRAP,"https://use.fontawesome.com/releases/v6.2.0/css/all.css"],
            suppress_callback_exceptions=True,
            assets_folder=self.settings['assets']   
        )
    
    def _run(self) -> None:
        self.dash.run_server(debug=True)

    def _get_nav_bar(self) -> html:
        nav_drop_down = dbc.DropdownMenu(
            [   dbc.DropdownMenuItem("Home", href="/Home"),
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
                                        [   html.Img(src=self.dash.get_asset_url('IconW.png'), height='50px', style={'padding-left':'1%','padding-top':'0%','padding-bottom':'0%'}),
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

    def _account_creation_modal(self) -> html:
        return dbc.Modal(
            [   dbc.ModalHeader("Initial Account Set-Up"),
                dbc.Card(
                    [   dbc.FormFloating(
                            [   dbc.Input(type="text", id='account_name'),
                                dbc.Label("Account Nickname"),
                                dbc.FormText("Enter a nickname for your account",color="secondary",),
                            ],
                            className="mb-3"
                        ),
                        dbc.FormFloating(
                            [   dbc.Input(type="text", id='account_holder'),
                                dbc.Label("Account Holder"),
                                dbc.FormText("Enter the name of the person who holds this account",color="secondary",),
                            ],
                            className="mb-3"
                        ),
                        dbc.Row(
                            [   dbc.Label("Account Type", html_for="account_type", width=4),
                                dbc.Col(
                                    dbc.RadioItems(
                                        id="account_type",
                                        options = [{"label": account_type, "value": account_type} for account_type in self.settings['account_types']],
                                        value=self.settings['account_types'][0]
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
            is_open=True,
        )
    
    def _default_layout(self, content:html) -> html:
        """
        Returns content in the default page structure. All pages will be rendered through this default layout.
        i.e. all pages will have the Navigation header and project footer

        Args:
            content (html): page data to render

        Returns:
            html: content wrapped in a default layout
        """    
        return html.Div(
            children=[
                dcc.Location(id='url', refresh=False),
                self._get_nav_bar(),
                dbc.Collapse([self._account_creation_modal()], id="navbar-collapse"),
                dcc.Store(data=self._account_config, id='memory', storage_type='local'), 
                html.Div(
                    content,
                    id='page-content',
                    style={'padding-top':'0px'}
                ),
            ]
        )

    def _get_layouts(self) -> None:
        self.dash.layout = self._default_layout(h_page)

        self.layouts = {'Home':{'tabs':{}},'Settings':{'tabs':{}}}

        if len(self._A_M._accounts) == 0:
            self.layouts['Home']['tabs']['overview'] = html.Div("No Accounts Found")
        else:
            self.layouts['Home']['tabs']['overview'] = self.get_tab_overview_layout(self._A_M._accounts[0])
        self.layouts['Home']['tabs']['accounts'] = self.get_tab_accounts_layout()

    def get_tab_overview_layout(self, selected_account):
        df = selected_account._T_M._df.copy()
        df['date'] = df.date.dt.date
        df['amount'] = df.amount.astype('float64')        
        ax = df.groupby('date', as_index=False).agg({'balance':'last'})
        fig = px.area(ax, x = 'date',y = 'balance')#, color="City", barmode="group")
        return tab_overview(df[['date','type','payment_type','amount','balance','description']].head(15), fig)

    def get_tab_accounts_layout(self):
        summary = self._A_M._return_accounts_summary()
        return tab_accounts(summary)
        


    def callbacks(self, dash:object):
        @dash.callback(Output('page-content', 'children'),[Input('url', 'pathname')])
        def display_page(pathname):
            """
            Change in url will result in this callback.
            Changes the page content based on the url change

            Args:
                pathname (str): url of page

            Returns:
                html: returns page based on provided url
            """    
            if pathname == '/Home':
                return h_page
            elif pathname == '/Settings':
                return html.Div('comingsooon')
            else:
                return html.Div(pathname)

        @dash.callback(Output('db-tab-content', 'children'), Input('db-tab', 'value'))
        def render_content(tab):
            """
            Render tab content based on the selected tab

            Args:
                tab (str): string value associated with the id: db-tab

            Returns:
                html: html content based on tab selected
            """    
            if tab == 'overview':
                return self.layouts['Home']['tabs']['overview']
            elif tab == 'accounts':
                return self.layouts['Home']['tabs']['accounts']

        @dash.callback(
            Output("first-time-set-up-modal", "is_open"), Output("account_name", "invalid"), Output("account_holder", "invalid"),
            Input('create-account','n_clicks'),
            State('account_name','value'),State('account_holder','value'),State('account_type','value'),State('account_provider','value'),State('memory','data'),
            prevent_initial_call = True
        )
        def store_encryption(create_n_clicks,account_name,account_holder,account_type,account_provider,mem):
            dash.logger.info(mem)
            if create_n_clicks>0:
                if None in [account_name,account_holder]:
                    account_name_invalid = False
                    account_holder_invalid = False
                    if not account_name:
                        account_name_invalid = True
                    if not account_holder:
                        account_holder_invalid = True                
                    return True, account_name_invalid, account_holder_invalid
                else:
                    dash.logger.info(self._A_M._accounts)
                    # self._A_M._add_account()
                    return False, False, False
            else:
                raise PreventUpdate

        # print('Please provide information below')
        # account_name = self._determine_nickname()
        # if not account_name: return

        # account_holder = self._determine_user(confirm_user)
        # if not account_holder: return
        
        # return Account(account_holder, account_name)




    def _check_save(self) -> bool:
        if self._account_config != self._A_M._config: 
            print('***'*20)
            print(self._account_config)
            print('---'*20)
            print(self._A_M._config)
            print('***'*20)
            return True

    def _save(self) -> None:
        self._rewrite_config(self._A_M._config)

    def _determine_config(self) -> dict:
        if os.path.isfile(self._account_config_path):
            return self._load_config()
        else:
            return {}

    def _create_config(self, config:dict) -> dict:
        json_obj = json.dumps(config, indent=4)
        with open(self._account_config_path,"w") as of:
            of.write(json_obj)
        return config

    def _load_config(self) -> dict:
        with open(self._account_config_path,'r') as of:
            json_obj = json.load(of)
        return json_obj

    def _rewrite_config(self, config:dict) -> None:
        self._create_config(config)
    
    def _load_accounts(self) -> Account_Manager:
        return Account_Manager(self._account_config)


