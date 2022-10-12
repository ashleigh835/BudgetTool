from app.common.config_info import Config
from app.account import Account
from app.helpers.date_helpers import weekdays
from app.helpers.readable_helpers import currency_readable_styled, currency_readable_styled, monthly_readable
from app.layouts.common import account_card

from dash import dcc, html, dash_table, ctx, MATCH, ALL
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from datetime import date, timedelta
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import base64
import io

tab_Style = {
    'padding': '0',
    'height': '44px',
    'line-height': '44px'
}

page_layout = html.Div(
    [   dcc.Tabs(
            id='tab', 
            # value='transactions',
            value='sched transactions' ,
            children=[
                dcc.Tab(label='Transactions', value='transactions',style=tab_Style,selected_style=tab_Style),
                dcc.Tab(label='Scheduled Transactions', value='sched transactions',style=tab_Style,selected_style=tab_Style),
            ],
        ),
        html.Hr(),
        html.Div(id='tab-content')
    ]
)

scheduled_transaction_frequencies_dict = {
    'monthly': {
        'title':'Monthly',
        'description':'Transactions recurring on a monthly basis', 
        'sub-description':'Day of the month which the transaction will occur on (use END for last day of the month)', 
    },
    'weekly' : {
        'title':'Weekly',
        'description':'Transactions recurring on a weekly basis', 
        'sub-description':'Day of the week which the transactions will occur on', 
    },
    'daily' : {
        'title':'Daily',
        'description':'Transactions recurring on a daily basis', 
        'sub-description':'', 
    },
    'one-off' : {
        'title':'One-off',
        'description':'Transactions scheduled to occur on specific dates',
        'sub-description':'Date transaction will occur',
    },
}

scheduled_transaction_types_ls = Config().settings()['scheduled_transaction_types']

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

scheduled_transaction_subfrequency_selection={
    'monthly' : html.Div(
        [   html.Small("Day:"),
            dbc.RadioItems(
                id="ammend-scheduled-transaction-subfrequency-type-radio",
                inline=True,
                options = [
                    {'label':'1-31','value':'1-31'},
                    {'label':'End','value':'End'},
                ],
                value = '1-31'
            ),
            html.Div(
                [   dbc.Input(type="number", min=1, max=31, step=1, size='sm', className="mb-3", id='ammend-scheduled-transaction-subfrequency-type-monthly-days-input'),
                    dbc.Tooltip(
                        scheduled_transaction_frequencies_dict['monthly']['sub-description'],
                        target="ammend-scheduled-transaction-subfrequency-type-monthly-days-input",
                    )
                ],
                id='ammend-scheduled-transaction-subfrequency-type-monthly', style={'display':'none'},
            )   
        ],
        id='ammend-scheduled-transaction-subfrequency-monthly',
        style={'display':'none'}
    ),
    'weekly' : html.Div(
        [   dcc.Dropdown(
                [ wkd for wkd in weekdays()],
                id="ammend-scheduled-transaction-subfrequency-type-dropdown",
                placeholder='Weekday',
                searchable=False, 
                optionHeight=20
            ),
            dbc.Tooltip(
                scheduled_transaction_frequencies_dict['weekly']['sub-description'],
                target="ammend-scheduled-transaction-subfrequency-type-dropdown",
            ),
        ],
        id='ammend-scheduled-transaction-subfrequency-weekly',
        style={'display':'none'}
    ),
    'daily' : html.Div(id='ammend-scheduled-transaction-subfrequency-daily',style={'display':'none'}),
    'one-off' : html.Div(
        [   dbc.Row(
                [   dcc.DatePickerSingle(
                        id='ammend-scheduled-transaction-subfrequency-type-date-picker',
                        min_date_allowed=date.today()+timedelta(days=1),
                        initial_visible_month=date.today()+timedelta(days=1),
                    ),
                    dbc.Tooltip(
                        scheduled_transaction_frequencies_dict['one-off']['sub-description'],
                        target="ammend-scheduled-transaction-subfrequency-type-date-picker",
                    ),
                ]
            )
        ],
        id='ammend-scheduled-transaction-subfrequency-one-off',
        style={'display':'none'}
    )
}

ammend_schedule_transaction_modal = dbc.Modal(
    [   dbc.ModalHeader("Ammend Scheduled Transaction"),
        dcc.Store(storage_type='session', clear_data=True, id='ammend-scheduled-transaction-index'),
        dcc.Store(storage_type='session', clear_data=True, id='ammend-scheduled-transaction-account'),
        dbc.Card(
            [   dbc.FormFloating(
                    [   dbc.Input(type="text", id='ammend-scheduled-transaction-nickname'),
                        dbc.Label("Nickname"),
                        dbc.FormText("Enter a snappy name for your transaction",color="secondary",),
                    ],
                    className="mb-3"
                ),   
                dbc.FormFloating(
                    [   dbc.Input(type="text", id='ammend-scheduled-transaction-description'),
                        dbc.Label("Description"),
                        dbc.FormText(["Enter a description ",html.I("(optional)")],color="secondary"),
                    ],
                    className="mb-3"
                ),   
                dbc.FormFloating(
                    [   dbc.Input(type="value", id='ammend-scheduled-transaction-amount'),
                        dbc.Label("Amount"),
                        dbc.FormText("Enter the transaction amount",color="secondary"),
                    ],
                    className="mb-3"
                ),
                dbc.Row(
                    [   dbc.Label("Type", html_for="ammend-scheduled-transaction-type", width=3),
                        dbc.Col(
                            dbc.RadioItems(
                                id="ammend-scheduled-transaction-type",
                                options = [{"label": st_type, "value": st_type} for st_type in scheduled_transaction_types_ls],
                                value=scheduled_transaction_types_ls[0]
                            ),
                            width=9,
                        ),
                    ],
                    className="mb-3",
                ),
                dbc.Accordion(
                    id='ammend-scheduled-transaction-accordian',
                    className='mb-3',
                    style = {'padding-left':'1%','padding-right':'1%'} ,
                    start_collapsed=True,
                    flush=True,
                    always_open=True 
                    
                ),
                dbc.Row(
                    dbc.Col(
                        [   dbc.Button(
                                'Add frequency',
                                id='ammend-scheduled-transaction-add-frequency',
                                size="sm",
                                className="ml-auto w-50 ",
                                color='primary',
                            ),
                            dbc.Button(
                                'Remove frequency',
                                id='ammend-scheduled-transaction-remove-frequency',
                                size="sm",
                                color='danger',
                                className="ml-auto w-50",
                            )
                        ],
                        width=12,
                        className = "d-flex align-items-center justify-content-center"
                    ),
                ),
                html.Div(
                    [   dcc.Store(id='scheduled-transaction-sub-freq', storage_type='session', clear_data=True),
                        dbc.Row(
                            [   html.Hr(),
                                dbc.Label("Frequency", html_for="ammend-scheduled-transaction-frequency-radio", width=3),
                                dbc.Col(
                                    dbc.RadioItems(
                                        id="ammend-scheduled-transaction-frequency-radio",
                                        options = [{"label": scheduled_transaction_frequencies_dict[st_type]['title'], "value": st_type} for st_type in scheduled_transaction_frequencies_dict.keys()],
                                        value=[l for l in scheduled_transaction_frequencies_dict.keys()][0]
                                    ),
                                    width=3,
                                ),
                                dbc.Col(
                                    width=6,
                                    children = [
                                        scheduled_transaction_subfrequency_selection['monthly'],
                                        scheduled_transaction_subfrequency_selection['weekly'],
                                        scheduled_transaction_subfrequency_selection['daily'],
                                        scheduled_transaction_subfrequency_selection['one-off']
                                    ],
                                    className="mb-3",
                                    style={"height": "5vh"}
                                ),
                            ],
                            style={'padding':'2%'}
                        ),
                        dbc.Row(dbc.Button('Add', color='success', id='btn-add-scheduled-transaction-subfrequency'))
                    ],
                    style={'display':'none'},
                    id='ammend-scheduled-transaction-frequency'
                ),
                html.Div(
                    [   dbc.Row(
                            [   html.Hr(),
                                dcc.Dropdown(
                                    id='ammend-scheduled-transaction-frequency-remove-dropdown', 
                                    multi=True, 
                                    searchable=False,
                                    placeholder="Choose a frequency rule to remove"
                                ),
                            ],
                            style={'padding':'2%'}
                        ),
                        dbc.Row(dbc.Button('Remove', color='danger', id='btn-remove-scheduled-transaction-subfrequency'))
                    ],
                    style={'display':'none'},
                    id='remove-scheduled-transaction-frequency'
                )
            ],
            style={ 'padding':'2%'}
        ),
        dbc.ModalFooter(
            [   dbc.Button("Delete Scheduled Transaction", id='btn-wipe-scheduled-transaction', className="ml-auto",color='danger', size="sm", outline=True),
                dbc.Button("Save Changes", id='btn-ammend-scheduled-transaction', className="ml-auto",color='success', size="sm", outline=True),
            ]
        ),        
        dbc.Toast(
            [html.P("Scheduled transaction updated!", className="mb-0")],
            id="save-toast",
            header="Changes Saved",
            duration=3000,
            is_open=False,
            style={"position": "fixed", "bottom": 66, "right": 10, "width": 350},
            icon='success'
        ),     
        dbc.Toast(
            [html.P("Frequency added to scheduled transaction staged changes! Save to permanaently update", className="mb-0")],
            id="add-freq-toast",
            header="Frequency Added",
            duration=3000,
            is_open=False, 
            icon='success',
            style={"position": "fixed", "bottom": 66, "right": 10, "width": 350},
        ),     
        dbc.Toast(
            [html.P("Frequency staged to be removed! Save to permanaently update", className="mb-0")],
            id="remove-freq-toast",
            header="Frequency Removed",
            duration=3000,
            is_open=False, 
            icon='danger',
            style={"position": "fixed", "bottom": 66, "right": 10, "width": 350},
        ),     
        dbc.Toast(
            [html.P("Scheduled transaction permanently removed!", className="mb-0")],
            id="remove-st-toast",
            header="Scheduled Transaction Removed",
            duration=3000,
            is_open=False, 
            icon='danger',
            style={"position": "fixed", "bottom": 66, "right": 10, "width": 350},
        )
    ],
    id="edit-scheduled-transaction-modal",
    size="md",
    is_open=False,
)

def tab_transactions_summary(accounts:dict={}) -> html:
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
                        dbc.Card(id='transaction-graph', className='mb-3'),
                        width=8
                    ),
                    dbc.Col(
                        dbc.Row(
                            [dbc.Card('test',id='hoverid',className='mb-3'),dbc.Card('test',className='mb-3')]
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

def tab_scheduled_transactions(accounts:dict={}) ->html:
    monthly_body = build_freq_all_cards('monthly', list(range(1, 32))+['End'])
    weekly_body = build_freq_all_cards('weekly', range(1, 8))
    daily_body = build_freq_all_cards('daily', ['Daily'])

    return html.Div(
        [   ammend_schedule_transaction_modal,
            dbc.Row(
                [   dbc.Col(width=3),
                    dbc.Col(
                        dcc.Dropdown([account for account in accounts.keys()], list(accounts.keys())[0], id='sched-transaction-selected-account-dropdown'),
                        className='mb-3',
                        width=6
                    ),
                    dbc.Col(width=3),
                ],
                className='mb-3',
                style = {'padding-left':'1%','padding-right':'1%'}                
            ),
            dbc.Row(
                [   dbc.Col(width=5),
                    dbc.Col(dbc.Button('Add Scheduled Transaction',id='sched-transaction-add-new', className='ml-auto w-100 ', size='sm'),width=2, className='justify-content-center mb-3 d-flex'),
                    dbc.Col(width=5),
                ]
            ),
            dbc.Accordion(
                [   dbc.AccordionItem([dbc.CardBody(monthly_body)], title="Monthly"),
                    dbc.AccordionItem([dbc.CardBody(weekly_body)], title="Weekly"),
                    dbc.AccordionItem([dbc.CardBody(daily_body)], title="Daily"),
                    dbc.AccordionItem([], title="One-Off", id='one-off-body')
                ],
                className='mb-3',
                style = {'padding-left':'1%','padding-right':'1%'} ,
                # start_collapsed=True,
                flush=True,
                always_open=True 
                
            )
        ]
    )

def build_scheduled_transaction_modal_frequency(scheduled_transaction:object) -> html:
    children=[]
    for freq in scheduled_transaction_frequencies_dict.keys():
        if freq in scheduled_transaction._frequency.keys():
            grand_children=[]
            for sub_freq in scheduled_transaction._frequency[freq]:
                if freq == 'monthly':
                    grand_children+=[
                        dbc.CardBody(monthly_readable(sub_freq)),
                    ]
                else:
                    grand_children+=[
                        dbc.CardBody(sub_freq),
                    ]
            
            children+=[dbc.AccordionItem(grand_children, title=scheduled_transaction_frequencies_dict[freq]['title'])]

    return children

def build_scheduled_transaction_badge(scheduled_transaction:object, card_id:int=0) -> html:    
    amt = scheduled_transaction._amount
    if scheduled_transaction._type == 'DEBIT':
        color = "danger"
        amt*=-1
    elif scheduled_transaction._type == 'CREDIT':
        color = "success"
    
    popover_footer_children, popover_footer_style = currency_readable_styled(amt)
    return [
        dbc.Badge(scheduled_transaction._summary, pill=True, color=color, className="me-1 text-decoration-none", id = f'st_{scheduled_transaction._index}_{card_id}'),
        dbc.Popover(
            [   dbc.PopoverBody(
                    [   html.H5(scheduled_transaction._summary),                        
                        dbc.Badge(
                            "manage",
                            color="info",
                            pill=True,
                            className="me-1 text-decoration-none position-absolute top-0 start-50 translate-middle",
                            href='#',
                            n_clicks = 0,
                            id={'type':f'manage_st','index':f'st_{scheduled_transaction._index}_{card_id}'}
                        ),
                        None or html.Small(scheduled_transaction._description, className="card-text text-muted")
                    ]
                ),
                dbc.CardFooter(children=html.B(popover_footer_children), style=popover_footer_style)
            ],
            target=f'st_{scheduled_transaction._index}_{card_id}',
            trigger="hover",
        )
    ]

def build_freq_all_cards(freq:str, card_ls:list ):
    children = []
    floor=1
    ceiling=len(card_ls)
    hidden_cards = None
    if ceiling == 1:
        return build_freq_cards(freq, card_ls, top=False, hidden_card_lim=6)

    for i in range(floor,ceiling,7):
        lower = i 
        uppr = i+7
        top = True

        if i == floor:
            top=False
        if i+7 > ceiling+1:
            uppr=ceiling+1
            hidden_cards = 7- len(card_ls[lower-1:uppr-1])

        children += [build_freq_cards(freq, card_ls[lower-1:uppr-1], top=top, hidden_card_lim=hidden_cards)]

    return children

def build_freq_cards(freq:str, ls:list, top:bool=True, hidden_card_lim:int=None) -> html:
    style={}
    if top:
        style['padding-top'] = '1%'
    
    cards = []
    for i in ls:
        if freq in ['monthly','daily','one-off']:
            head = i
        elif freq == 'weekly':
            head = weekdays()[i-1]
        cards += [
            dbc.Col(
                dbc.Card(
                    [   dbc.CardHeader(html.B(head)), 
                        dbc.CardBody(
                            dbc.ListGroup(flush=True,id={'type': f'{freq}_scheduled_transaction_item','index': str(i)})
                        ),
                        dbc.CardFooter(id={'type': f'{freq}_scheduled_transaction_footer','index': str(i)})
                    ],                
                    id={'type': f'{freq}_scheduled_transaction_card','index': str(i)},
                    style = {'height': '100%', 'display': 'block'}
                )
            )
        ]
    
    hidden_cards = []
    if hidden_card_lim:
        hidden_cards = [dbc.Col(
            dbc.Card(style = {'display': 'none'})
        ) for i in range(0,hidden_card_lim)]
    
    return dbc.Row(cards+hidden_cards, class_name='text-center', style = style,)

def account_visual_graph(selected_account:Account) -> object:
    if selected_account._T_M._df.empty:
        return None
    
    df = selected_account._T_M._df.copy()[['amount','type','date','description','payment_type','balance']]
    # df['month'] = df.date.dt.strftime('%Y-%m')
    # fig = px.box(df, x="month", y="balance")
    df['date'] = df.date.dt.date
    df['amount'] = df.amount.astype('float64')  
    
    # description_day_df = df.copy()
    # description_day_df['description_day'] = description_day_df['description']
    # description_day_df = description_day_df.groupby(['date'])['description_day'].apply('<br>'.join).reset_index()
    # description_day_df['description_day'] = '<br>'+description_day_df['description_day']        
    # df = df.merge(description_day_df,on='date',how='inner')

    # ax = df.groupby(['date','description_day'], as_index=False).agg({'balance':'last'})
    fig = px.area(df, x = 'date',y = 'balance')
    return dcc.Graph(className='mb-3', figure=fig) 
        #     fig = px.area(ax, x = 'date',y = 'balance')#, hover_data=["description_day"], 
        # #     hover_name='balance',
        # #     hover_data={
        # #         'date':True,
        # #         'balance':False,
        # #         'description_day':True
        # #         # 'sepal_length':':.2f', # customize hover for column of y attribute
        # #     },
        # # )#, color="City", barmode="group")
        # # fig = px.area(ax, x = 'date',y = 'balance', hover_name="country", hover_data=["continent", "pop"])

def account_visual_data(selected_account:Account) -> object:
    if selected_account._T_M._df.empty:
        return None

    df = selected_account._T_M._df.copy()[['amount','type','date','description','payment_type','balance']]
    df['date'] = df.date.dt.date
    df['amount'] = df.amount.astype('float64')  

    return dash_table.DataTable(
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

def callbacks(gui, dash:object):
    @dash.callback(
        Output("transaction-selected-account-detail", "children"),Output('transaction-graph','children'),Output('transaction-data','children'),
        Input("transaction-selected-account-dropdown", "value"), Input('upload-transactions', 'data'),
    )
    def render_content_transaction(selected_account_nickname, temp_data):
        selected_account = gui._A_M._determine_account_from_name(selected_account_nickname)
        data = gui._A_M._return_accounts_summary()
        
        account_detail = account_card(selected_account_nickname, data)
        fig = account_visual_graph(selected_account)
        dta = account_visual_data(selected_account)
        
        return account_detail, fig, dta
    
    @dash.callback(
        Output({'type': 'monthly_scheduled_transaction_item','index': MATCH}, 'children'),
        Output({'type': 'monthly_scheduled_transaction_footer','index': MATCH}, 'children'),
        Output({'type': 'monthly_scheduled_transaction_footer','index': MATCH}, 'style'),
        Input("sched-transaction-selected-account-dropdown", "value"), 
        State({'type': 'monthly_scheduled_transaction_item','index': MATCH}, 'id'),
        State({'type': 'monthly_scheduled_transaction_footer','index': MATCH}, 'children')
    )
    def render_content_scheduled_transaction_monthly(selected_account_nickname,id,footer):
        selected_account = gui._A_M._determine_account_from_name(selected_account_nickname)
        st_list = selected_account.get_scheduled_transactions_from_key('monthly',id['index'])
        children = []
        footer = footer or []
        card_amt = 0

        for st in st_list:
            children += build_scheduled_transaction_badge(st, id['index'])
            if st._type == 'DEBIT':
                card_amt+=st._amount*-1
            elif st._type == 'CREDIT':
                card_amt+=st._amount                
        
        if len(children)>0: 
            temp_footer, footer_style = currency_readable_styled(card_amt)
            footer = [html.B(temp_footer)]

        if not children:
            return children, footer, {'display': 'none'}
        else: 
            return (
                [
                    html.Div(html.Span(children), style={'display':'flex','flex-direction':'column','min-height':'10vh'}),
                    html.Div(className="wrapper",style={'flex':1})
                ],
                footer,
                footer_style
            )

    @dash.callback(
        Output({'type': 'weekly_scheduled_transaction_item','index': MATCH}, 'children'),
        Output({'type': 'weekly_scheduled_transaction_footer','index': MATCH}, 'children'),
        Output({'type': 'weekly_scheduled_transaction_footer','index': MATCH}, 'style'),
        Input("sched-transaction-selected-account-dropdown", "value"), 
        State({'type': 'weekly_scheduled_transaction_item','index': MATCH}, 'id'),
        State({'type': 'weekly_scheduled_transaction_footer','index': MATCH}, 'children')
    )
    def render_content_scheduled_transaction_weekly(selected_account_nickname,id,footer):
        selected_account = gui._A_M._determine_account_from_name(selected_account_nickname)
        st_list = selected_account.get_scheduled_transactions_from_key('weekly',weekdays()[int(id['index'])-1])
        children = []
        footer = footer or []
        card_amt = 0

        for st in st_list:
            children += build_scheduled_transaction_badge(st, id['index'])
            if st._type == 'DEBIT':
                card_amt+=st._amount*-1
            elif st._type == 'CREDIT':
                card_amt+=st._amount                
        
        if len(children)>0: 
            temp_footer, footer_style = currency_readable_styled(card_amt)
            footer = [html.B(temp_footer)]

        if not children:
            return children, footer, {'display': 'none'}
        else: 
            return (
                [   html.Div(html.Span(children), style={'display':'flex','flex-direction':'column','min-height':'10vh'}),
                    html.Div(className="wrapper",style={'flex':1})
                ],
                footer,
                footer_style
            )

    @dash.callback(
        Output({'type': 'daily_scheduled_transaction_item','index': MATCH}, 'children'),
        Output({'type': 'daily_scheduled_transaction_footer','index': MATCH}, 'children'),
        Output({'type': 'daily_scheduled_transaction_footer','index': MATCH}, 'style'),
        Input("sched-transaction-selected-account-dropdown", "value"), 
        State({'type': 'daily_scheduled_transaction_item','index': MATCH}, 'id'),
        State({'type': 'daily_scheduled_transaction_footer','index': MATCH}, 'children')
    )
    def render_content_scheduled_transaction_daily(selected_account_nickname,id,footer):
        selected_account = gui._A_M._determine_account_from_name(selected_account_nickname)
        st_list = selected_account.get_scheduled_transactions_from_key('daily')
        children = []
        footer = footer or []
        card_amt = 0

        for st in st_list:
            children += build_scheduled_transaction_badge(st, id['index'])
            if st._type == 'DEBIT':
                card_amt+=st._amount*-1
            elif st._type == 'CREDIT':
                card_amt+=st._amount                
        
        if len(children)>0: 
            temp_footer, footer_style = currency_readable_styled(card_amt)
            footer = [html.B(temp_footer)]

        if not children:
            return children, footer, {'display': 'none'}
        else: 
            return (
                [   html.Div(html.Span(children), style={'display':'flex','flex-direction':'column','min-height':'10vh'}),
                    html.Div(className="wrapper",style={'flex':1})
                ],
                footer, 
                footer_style
            )

    @dash.callback(
        Output('one-off-body', 'children'),
        Input("sched-transaction-selected-account-dropdown", "value"), 
    )
    def render_content_scheduled_transaction_one_off_cards(selected_account_nickname):
        selected_account = gui._A_M._determine_account_from_name(selected_account_nickname)
        st_list = selected_account.get_scheduled_transactions_from_key('one-off')
        date_ls = []
        for st in st_list:
            date_ls += st._frequency['one-off']
        return build_freq_all_cards('one-off', date_ls)

    @dash.callback(
        Output({'type': 'one-off_scheduled_transaction_item','index': MATCH}, 'children'),
        Output({'type': 'one-off_scheduled_transaction_footer','index': MATCH}, 'children'),
        Output({'type': 'one-off_scheduled_transaction_footer','index': MATCH}, 'style'),
        Input("sched-transaction-selected-account-dropdown", "value"), 
        State({'type': 'one-off_scheduled_transaction_item','index': MATCH}, 'id'),
        State({'type': 'one-off_scheduled_transaction_footer','index': MATCH}, 'children')
    )
    def render_content_scheduled_transaction_one_off_card_content(selected_account_nickname,id,footer):
        selected_account = gui._A_M._determine_account_from_name(selected_account_nickname)
        st_list = selected_account.get_scheduled_transactions_from_key('one-off',id['index'])
        children = []
        footer = footer or []
        card_amt = 0

        for st in st_list:
            children += build_scheduled_transaction_badge(st, id['index'])
            if st._type == 'DEBIT':
                card_amt+=st._amount*-1
            elif st._type == 'CREDIT':
                card_amt+=st._amount                
        
        if len(children)>0: 
            temp_footer, footer_style = currency_readable_styled(card_amt)
            footer = [html.B(temp_footer)]

        if not children:
            return children, footer, {'display': 'none'}
        else: 
            return (
                [   html.Div(html.Span(children), style={'display':'flex','flex-direction':'column','min-height':'10vh'}),
                    html.Div(className="wrapper",style={'flex':1})
                ],
                footer, 
                footer_style
            )

    @dash.callback(
        Output('edit-scheduled-transaction-modal','is_open'),
        Output('ammend-scheduled-transaction-nickname','value'),
        Output('ammend-scheduled-transaction-description','value'),
        Output('ammend-scheduled-transaction-amount','value'),
        Output('ammend-scheduled-transaction-type','value'),
        Output('ammend-scheduled-transaction-accordian','children'),
        Output('ammend-scheduled-transaction-index','data'),
        Output('ammend-scheduled-transaction-account','data'),
        Output('ammend-scheduled-transaction-remove-frequency','style'),
        Input({'type':f'manage_st','index': ALL}, 'n_clicks'),
        Input('sched-transaction-add-new','n_clicks'),
        State("sched-transaction-selected-account-dropdown", "value"), 
        prevent_initial_call = True
    )
    def manage_scheduled_transaction(manage_n,add_new_n,selected_account_nickname):
        #Title: Ammend vs Add
        #btn: Save Changes vs Save
        #can't add frequency rules until all fields have been added

        # input Output('remove-st-toast','is_open'), -> close modal
        print(ctx.triggered_id)
        if ctx.triggered_id == 'sched-transaction-add-new':
            if add_new_n !=0 :
                print(add_new_n)
                # selected_account = gui._A_M._determine_account_from_name(selected_account_nickname)
                # scheduled_transaction = selected_account._create_scheduled_transaction()
                return (
                    True,
                    None, 
                    None, 
                    None,
                    'DEBIT',
                    None,
                    None, # will need to carry this somehow maybe?
                    selected_account_nickname,
                    {'display':'none'}
                )

        else:
            if manage_n != [0]*len(manage_n):
                
                indx =int(ctx.triggered_id['index'].split('_')[1])
                selected_account = gui._A_M._determine_account_from_name(selected_account_nickname)
                scheduled_transaction = selected_account._determine_scheduled_transaction_from_index(indx)

                style = None
                if not scheduled_transaction._frequency:
                    style={'display':'none'}

                acc = build_scheduled_transaction_modal_frequency(scheduled_transaction)
                print(scheduled_transaction)
                return (
                    True, 
                    [scheduled_transaction._summary], 
                    [scheduled_transaction._description], 
                    [scheduled_transaction._amount], 
                    scheduled_transaction._type, 
                    acc,
                    indx,
                    selected_account_nickname,
                    style
                )
            else:
                raise PreventUpdate

    @dash.callback(
        Output('ammend-scheduled-transaction-frequency','style'),
        Output('ammend-scheduled-transaction-add-frequency','color'),
        Output('ammend-scheduled-transaction-add-frequency','children'),        
        Output('remove-scheduled-transaction-frequency','style'),
        Output('ammend-scheduled-transaction-remove-frequency','color'),
        Output('ammend-scheduled-transaction-remove-frequency','children'),
        Output('ammend-scheduled-transaction-nickname','invalid'),
        Output('ammend-scheduled-transaction-amount','invalid'),
        Input('ammend-scheduled-transaction-add-frequency','n_clicks'),         
        Input('ammend-scheduled-transaction-remove-frequency','n_clicks'),
        State('ammend-scheduled-transaction-add-frequency','children'), 
        State('ammend-scheduled-transaction-remove-frequency','children'),
        State('ammend-scheduled-transaction-nickname','value'),
        State('ammend-scheduled-transaction-amount','value'),
        State('ammend-scheduled-transaction-index','data'),
        State('ammend-scheduled-transaction-account','data'),
        prevent_initial_call = True
    )
    def render_frequencies(add_n,rem_n,add_btn_str,rem_btn_str, nickname, amount, st_index, selected_account_nickname):
        amt_invalid=False
        sum_invalid=False
        if (not nickname):sum_invalid=True
        if (not amount):amt_invalid=True

        if ctx.triggered_id == 'ammend-scheduled-transaction-add-frequency':
            if add_btn_str == 'Hide':
                return {'display':'none'}, 'primary', 'Add frequency', {'display':'none'}, 'danger', 'Remove frequency', sum_invalid, amt_invalid
            else:
                if amt_invalid | sum_invalid:
                    return {'display':'none'}, 'primary', 'Add frequency', {'display':'none'}, 'danger', 'Remove frequency', sum_invalid, amt_invalid
                else:
                    if not st_index:
                        selected_account = gui._A_M._determine_account_from_name(selected_account_nickname)
                        scheduled_transaction = selected_account._determine_scheduled_transaction_from_index(st_index)
                        if not scheduled_transaction:
                            print(f'adding scheduled transaction')
                            selected_account._create_scheduled_transaction(t_summary=nickname, t_amount=amount)
                            # Need to store the index to be able to update...

                    return {'padding':'2%'}, 'secondary', 'Hide', {'display':'none'}, 'danger', 'Remove frequency', sum_invalid, amt_invalid
        elif ctx.triggered_id == 'ammend-scheduled-transaction-remove-frequency':
            if rem_btn_str == 'Hide':
                return {'display':'none'}, 'primary', 'Add frequency', {'display':'none'}, 'danger', 'Remove frequency', sum_invalid, amt_invalid
            else:
                return {'display':'none'}, 'primary', 'Add frequency', {'padding':'2%'}, 'secondary', 'Hide', sum_invalid, amt_invalid
    
    @dash.callback(
        Output('ammend-scheduled-transaction-subfrequency-monthly','style'),  
        Output('ammend-scheduled-transaction-subfrequency-type-monthly','style')  ,
        Output('ammend-scheduled-transaction-subfrequency-weekly','style'),  
        Output('ammend-scheduled-transaction-subfrequency-daily','style'),
        Output('ammend-scheduled-transaction-subfrequency-one-off','style'),
        Input('ammend-scheduled-transaction-frequency-radio','value'),
        Input('ammend-scheduled-transaction-subfrequency-type-radio','value')
    )
    def render_frequency_subtype(freq, sub_freq_type):
        if freq == 'monthly':
            if sub_freq_type == '1-31':
                return None, None, {'display':'none'}, {'display':'none'}, {'display':'none'}
            elif sub_freq_type == 'End':
                return None, {'display':'none'}, {'display':'none'}, {'display':'none'}, {'display':'none'}

        elif freq == 'weekly':            
            return {'display':'none'}, {'display':'none'}, None, {'display':'none'}, {'display':'none'}
        
        elif freq == 'daily':
            return {'display':'none'}, {'display':'none'}, {'display':'none'}, None, {'display':'none'}
        
        elif freq == 'one-off':
            return {'display':'none'}, {'display':'none'}, {'display':'none'}, {'display':'none'}, None
            
    @dash.callback(
        Output('scheduled-transaction-sub-freq','data'),
        Input('ammend-scheduled-transaction-frequency-radio','value'),
        Input('ammend-scheduled-transaction-subfrequency-type-radio','value'),
        Input('ammend-scheduled-transaction-subfrequency-type-monthly-days-input','value'),
        Input('ammend-scheduled-transaction-subfrequency-type-dropdown','value'),
        Input('ammend-scheduled-transaction-subfrequency-type-date-picker','date'),
        prevent_initial_call=True
    )
    def store_subfreq(freq, sub_freq_type, monthly_freq_days, weekly_freq, one_off_date):
        if freq == 'monthly':
            if sub_freq_type == '1-31':
                return str(monthly_freq_days)
            elif sub_freq_type == 'End':
                return 'End'
        elif freq == 'weekly':            
            return weekly_freq        
        elif freq == 'daily':
            return 'daily'        
        elif freq == 'one-off':
            return one_off_date

    @dash.callback(
        Output('add-freq-toast','is_open'),
        Input('btn-add-scheduled-transaction-subfrequency','n_clicks'),
        State('ammend-scheduled-transaction-frequency-radio','value'),
        State('scheduled-transaction-sub-freq','data'),
        State('ammend-scheduled-transaction-index','data'),
        State('ammend-scheduled-transaction-account','data'),
        prevent_initial_call=True
    )
    def add_sub_frequency(n, freq, sub_freq, st_index, selected_account_nickname):  
        selected_account = gui._A_M._determine_account_from_name(selected_account_nickname)
        scheduled_transaction = selected_account._determine_scheduled_transaction_from_index(st_index)
        if n != 0:
            if sub_freq:
                scheduled_transaction._update_frequency(freq, sub_freq)
                return True
        
        raise PreventUpdate

    @dash.callback(
        Output('ammend-scheduled-transaction-frequency-remove-dropdown','options'),
        Input('ammend-scheduled-transaction-remove-frequency','n_clicks'),
        State('ammend-scheduled-transaction-index','data'),
        State('ammend-scheduled-transaction-account','data'),
        prevent_initial_call=True
    )
    def load_remove_sub_frequency_options(n, st_index, selected_account_nickname):
        selected_account = gui._A_M._determine_account_from_name(selected_account_nickname)
        scheduled_transaction = selected_account._determine_scheduled_transaction_from_index(st_index)
        options = []
        for freq in scheduled_transaction._frequency.keys():
            options += [{'label': freq, 'value': freq,'disabled': True}]
            for sub_freq in scheduled_transaction._frequency[freq]:
                options += [{'label':sub_freq, 'value':f'{freq}_{sub_freq}'}]

        return options
    
    @dash.callback(
        Output('remove-freq-toast','is_open'),
        Input('btn-remove-scheduled-transaction-subfrequency','n_clicks'),
        State('ammend-scheduled-transaction-frequency-remove-dropdown','value'),
        State('ammend-scheduled-transaction-index','data'),
        State('ammend-scheduled-transaction-account','data'),
        prevent_initial_call=True
    )
    def remove_sub_frequency(n, sub_freq_rule_ls, st_index, selected_account_nickname): 
        if n != 0:
            if sub_freq_rule_ls:
                selected_account = gui._A_M._determine_account_from_name(selected_account_nickname)
                scheduled_transaction = selected_account._determine_scheduled_transaction_from_index(st_index)
                for sub_freq_rule in sub_freq_rule_ls:
                    freq = sub_freq_rule.split('_')[0]
                    sub_freq = sub_freq_rule.split('_')[1]
                    scheduled_transaction._remove_frequency(freq,sub_freq)
                return True
        
        raise PreventUpdate

    @dash.callback(
        Output('save-toast','is_open'),
        Input('btn-ammend-scheduled-transaction','n_clicks'),
        State('ammend-scheduled-transaction-nickname','value'),
        State('ammend-scheduled-transaction-description','value'),
        State('ammend-scheduled-transaction-amount','value'),
        State('ammend-scheduled-transaction-type','value'),
        State('ammend-scheduled-transaction-index','data'),
        State('ammend-scheduled-transaction-account','data'),
        prevent_initial_call=True
    )
    def save_scheduled_transaction_changes(n, nickname, description, amount, st_type, st_index, selected_account_nickname):
        if n!=0:
            def clean(val:object):
                if type(val) == list:
                    return val[0]
                else:
                    return val

            selected_account = gui._A_M._determine_account_from_name(selected_account_nickname)
            scheduled_transaction = selected_account._determine_scheduled_transaction_from_index(st_index)
            if clean(nickname) != scheduled_transaction._summary:
                gui.dash.logger.info(f'scheduled transaction change: nickname [{scheduled_transaction._summary}] -> [{nickname}]')
                scheduled_transaction._summary = clean(nickname)

            if clean(description) != scheduled_transaction._description:
                gui.dash.logger.info(f'scheduled transaction change: nickname [{scheduled_transaction._description}] -> [{description}]')
                scheduled_transaction._description = clean(description)

            if clean(amount) != scheduled_transaction._amount:
                gui.dash.logger.info(f'scheduled transaction change: nickname [{scheduled_transaction._amount}] -> [{amount}]')
                scheduled_transaction._amount = clean(amount)

            if clean(st_type)!= scheduled_transaction._type:
                gui.dash.logger.info(f'scheduled transaction change: nickname [{scheduled_transaction._type}] -> [{st_type}]')
                scheduled_transaction._type = clean(st_type)

            if gui._check_save(): 
                gui._save() 
                return True
            else:
                print('Nothing to Save')    

        raise PreventUpdate

    @dash.callback(
        Output('remove-st-toast','is_open'),
        Input('btn-wipe-scheduled-transaction','n_clicks'),
        State('ammend-scheduled-transaction-index','data'),
        State('ammend-scheduled-transaction-account','data'),
        prevent_initial_call=True
    )
    def delete_scheduled_transaction(n, st_index, selected_account_nickname):
        if n != 0:
            selected_account = gui._A_M._determine_account_from_name(selected_account_nickname)
            scheduled_transaction = selected_account._determine_scheduled_transaction_from_index(st_index)
            selected_account._remove_scheduled_transaction(scheduled_transaction)
            
            if gui._check_save(): 
                gui._save() 
                return True
        
        raise PreventUpdate


        #     #    graph = dcc.Graph(id='transaction-graph', figure=fig, className='mb-3')        
        # @dash.callback(
        #     Output('hoverid', 'children'),
        #     [Input('transaction-graph', 'hoverData')],
        #     prevent_initial_call = True
        # )
        # def display_hover_data(hoverData):
        #     # print(hoverData['points'][1])
        #     # return json.dumps(hoverData, indent=2)   
        #     return html.Div(hoverData['points'][0]['customdata'])
    
    @dash.callback(
        Output('upload-transactions', 'data'),
        Input('upload-transactions', 'contents'),
        State('upload-transactions', 'filename'),
        State("transaction-selected-account-dropdown", "value"),
        prevent_initial_call = True
        )
    def upload_transactions(list_of_contents, list_of_names,selected_account_nickname):
        selected_account = gui._A_M._determine_account_from_name(selected_account_nickname)
        if list_of_contents and list_of_names:
            content_type, content_string = list_of_contents.split(',')

            decoded = base64.b64decode(content_string)
            if ('csv' in list_of_names) | ('CSV' in list_of_names):
                df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), index_col=False)
                selected_account._T_M._load_transactions_from_df(df)
                gui._get_layouts()
            elif 'xls' in list_of_names:
                df = pd.read_excel(io.BytesIO(decoded))
                gui._get_layouts()  
