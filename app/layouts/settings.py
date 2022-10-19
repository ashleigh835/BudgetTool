from dash import dcc, html

tab_Style = {
    'padding': '0',
    'height': '44px',
    'line-height': '44px'
}
page_layout = html.Div(
    [   dcc.Tabs(
            id='tab', 
            value='Account Management',
            children=[
                dcc.Tab(label='Account Management', value='Account Management',style=tab_Style,selected_style=tab_Style),
                dcc.Tab(label='Temp', value='Temp',style=tab_Style,selected_style=tab_Style),
            ],
        ),
        html.Hr(),
        html.Div(id='tab-content')
    ]
)
