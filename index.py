from app.app import app
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

# Navigation Bar Drop Down Menu - navigate to Home or Settings pages
nav_drop_down = dbc.DropdownMenu(
    [   dbc.DropdownMenuItem("Home", href="/Home"),
        dbc.DropdownMenuItem(divider=True),
        dbc.DropdownMenuItem("Settings", href="/Settings"),
    ],
    label="Menu",
    className="ml-auto flex-nowrap mt-3 mt-md-0",
    id="menu_drop_down",
)

# Navigation Bar layout - conists of the icon, Title and dropdown menu
navbar = dbc.Navbar(
    [   # dcc.Store(id='encryption-key', storage_type='session'),
        # dcc.Store(data=False, id='encryption-key-set', storage_type='session',),
        # dcc.Store(data={'Wallets' : {'APIs' : {},'Addresses' : {}}}, id='memory', storage_type='local'), #, clear_data =True),
        # dcc.Store(data=False, id='settings_encryption_trigger', storage_type='session'),
        html.Div(
            dbc.Row(
                [   dbc.Col(html.Img(src=app.get_asset_url('IconW.png'), height='50px',style = {'padding-left':'30%'})),
                    dbc.Col(dbc.NavbarBrand("Budget Tool",className="ml-2",style = {'font-size': 30, 'padding-left':'3%'})),
                ],
                # no_gutters = True
            ),
        ),
        dbc.Collapse([nav_drop_down], id="navbar-collapse", navbar=True),

    ],
    color='dark',
    dark=True,
    fixed='top'
)

# Project Footer
footer = html.Footer(
    [   """This project is licensed under the terms of the GNU AFFERO GENERAL PUBLIC LICENSE (V3).""",                
        dcc.Markdown("""Icons made by [Eucalyp](https://www.flaticon.com/authors/eucalyp) from [Flaticon](https://www.flaticon.com/)""")
    ],
    style = {'font-size': 10}
)

def default_layout(content):
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

            dbc.Row(
                [dbc.Col(navbar)],
                align='center'
            ),


            html.Div(
                content,
                id='page-content',
                style={'padding-top':'70px'}
            ),

            html.Div(
                footer,
                style={
                    "position": "fixed",
                    "bottom": 0,
                    "left": 0,
                    "right": 0,
                    'padding-left':'1%',
                    'padding-right':'1%'
                }        
            )
        ]
    )
    
tab_Style = {
    'padding': '0',
    'height': '44px',
    'line-height': '44px'
}
db_layout = html.Div(
    [   # dcc.Store(id='daily-prices-df', storage_type='session',clear_data=True),
        # dcc.Store(id='balance-df', storage_type='session'),
        dcc.Tabs(
            id='db-tab', 
            value='bal', 
            children=[
                dcc.Tab(label='Overview', value='overview',style=tab_Style,selected_style=tab_Style),
                dcc.Tab(label='Accounts', value='accounts',style=tab_Style,selected_style=tab_Style),
            ],
        ),
        html.Hr(),
        html.Div(id='db-tab-content')
    ]
)
ls_layout = html.Div(
    [   dcc.Tabs(
            id='settings-tab', 
            value='Config', 
            children=[
                dcc.Tab(label='Account Settings', value='Account',style=tab_Style,selected_style=tab_Style),
                dcc.Tab(label='Transaction Settings', value='Transaction',style=tab_Style,selected_style=tab_Style),
            ],
        ),
        html.Hr(),
        html.Div(id='settings-tab-content-settings'),
    ]
)


# Render page through the default project layout. Initializes with the Home layout
app.layout = default_layout(db_layout)
    

@app.callback(Output('page-content', 'children'),[Input('url', 'pathname')])
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
        return db_layout
    elif pathname == '/Settings':
        return ls_layout
    else:
        return html.Div(pathname)

if __name__ == '__main__':
    app.run_server(debug=True)
