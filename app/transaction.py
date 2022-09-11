import pandas as pd
import numpy as np

class Transaction(object):
    _supported_providers = []

    def __init__(self, amount, type, date, description, payment_type, balance, scheduled=False, forecasted=False, **kwargs) -> None:
        self._amount = amount
        self._type = type
        self._date = date
        self._description = description
        self._payment_type = payment_type
        self._balance = balance
        self._scheduled = scheduled
        self._forecasted = forecasted

        self._df_entry =  self._create_df_entry()
        self._df_entry['date'] = self._df_entry.date.astype('datetime64')
        self._df_entry['balance'] = pd.to_numeric(self._df_entry.balance, errors='coerce')
        pass

    def __init_subclass__(cls) -> None:
        cls._supported_providers += cls.supported_providers
        pass

    def _translate(self, kwargs) -> None:
        conversion_dict = kwargs.copy()
        for transaction_arg in self.mapping:
            for arg in kwargs:
                if arg == self.mapping[transaction_arg]: 
                    conversion_dict[transaction_arg] = kwargs[arg]
        
        return super(self.__class__, self).__init__(**conversion_dict)     

    def _create_df_entry(self):
        return pd.DataFrame({
            'amount' : self._amount,
            'type' : self._type,
            'date' : self._date,
            'description' : self._description,
            'payment_type' : self._payment_type,
            'balance' : self._balance,
            'scheduled' : self._scheduled,
            'forecasted' : self._forecasted
        }, index=[0])

class Trasaction_Type_1(Transaction):
    supported_providers = ['Chase']
    mapping = { 
        'type' : 'Details' ,
        'date' : 'Posting Date' ,
        'description' : 'Description' ,
        'amount' : 'Amount' ,
        'payment_type' : 'Type' ,
        'balance' : 'Balance' 
    }
    conversion_dict = {}

    def __init__(self, kwargs) -> None:        
        return self._translate(kwargs)
        
class Trasaction_Type_2(Transaction):
    supported_providers = ['Lloyds']
    mapping = { 
        'type' : 'Details' ,
        'date' : 'Posting Date' ,
        'description' : 'Description' ,
        'amount' : 'Amount' ,
        'payment_type' : 'Type' ,
        'balance' : 'Bal' 
    }
    conversion_dict = {}

    def __init__(self, kwargs) -> None:       
        return self._translate(kwargs)

class Transaction_Manager(object):
    def __init__(self, df:pd.DataFrame()=pd.DataFrame()) -> None:
        self._transactions=[]
        self._df = df
        pass

    # @property
    # def _config(self) -> dict:
    #     _config = {}
    #     for transaction in self._accounts:
    #         if account._holder in _config.keys(): 
    #             _config[account._holder] += account._config[account._holder]
    #         else:
    #             _config[account._holder] = account._config[account._holder]
    #     return _config

    def _find_first_and_last_transactions(self, df:pd.DataFrame()=pd.DataFrame()) -> pd.DataFrame():
        """_summary_ REQUIRES df with field: date with dtype datetime64ns
        """        
        if df.empty:
            df = self._df

        if 'date' not in df.columns:
            raise Exception( 'Column `date` was missing')
        if not np.issubdtype(df.date.dtype, np.datetime64):
            raise TypeError( 'bad dtype for column `date`. Column should be datetime64[ns]')

        date_ls = [date.date() for date in df.date.sort_values(ascending=True).drop_duplicates()]

        new_cols = {
            'first':{'type':bool,'default':False},
            'last':{'type':bool,'default':False},
            'order':{'type':float,'default':np.nan}
            }

        for col in new_cols.keys():
            if col not in df.columns: 
                df[col]=new_cols[col]['default']
                df[col]=df[col].astype(new_cols[col]['type'])

        # loop through each date newest to oldest
        for i in range(len(date_ls)-1, -1, -1):
            dte = date_ls[i]
            dte_df = df[df.date.dt.date == dte]

            if i > 0:
                dte_compare = {'prev' : date_ls[i-1]}
            else:
                dte_compare = {'next' : date_ls[i+1]}

            _no_transactions = len(dte_df) 
            if _no_transactions == 1 :
                df.loc[dte_df.index, 'order'] = 0
                df.loc[dte_df.index, 'first'] = True
                df.loc[dte_df.index, 'last'] = True
            else:
                found = {'first' : False, 'last' : False}
                # Loop through each row for that date, checking if it's the first/ last transaction by comparing the balance + amount vs prev/next balance
                for index, row_dte in dte_df.iterrows():
                    if True not in found.values():
                        if 'prev' in dte_compare.keys():
                            last_df = df[
                                ( (df.date.dt.date == dte_compare['prev']) & (df.balance == round(row_dte.balance-row_dte.amount,2)) ) |
                                ( (df.date.dt.date == dte_compare['prev']) & (df['last']) )
                            ]
                            if not last_df.empty:
                                df.loc[last_df.head(1).index, 'order'] = len(df[(df.date.dt.date == dte_compare['prev'])])-1
                                df.loc[last_df.head(1).index, 'last'] = True

                                df.loc[index, 'order'] = 0
                                df.loc[index, 'first'] = True
                                
                                found['first'] = True
                        elif 'next' in dte_compare.keys():
                            first_df = df[
                                ( (df.date.dt.date == dte_compare['next']) & (df.balance == round(row_dte.balance+df.amount,2)) ) |
                                ( (df.date.dt.date == dte_compare['next']) & (df['first']) )
                            ]
                            if not first_df.empty:
                                df.loc[first_df.head(1).index, 'order'] = 0
                                df.loc[first_df.head(1).index, 'first'] = True

                                df.loc[index, 'order'] = len(df[(df.date.dt.date == dte)])-1
                                df.loc[index, 'last'] = True
                                
                                found['last'] = True
        return df

    def _order_middle_transactions(self, df:pd.DataFrame()=pd.DataFrame()) -> pd.DataFrame():    
        """_summary_ REQUIRES df with field: date with dtype datetime64ns
        """        
        if df.empty:
            df = self._df

        if 'date' not in df.columns:
            raise Exception( 'Column `date` was missing')
        if not np.issubdtype(df.date.dtype, np.datetime64):
            raise TypeError( 'bad dtype for column `date`. Column should be datetime64[ns]')

        date_ls = [date.date() for date in df.date.sort_values(ascending=True).drop_duplicates()]

        new_cols = {
            'first':{'type':bool,'default':False},
            'last':{'type':bool,'default':False},
            'order':{'type':float,'default':np.nan}
            }

        for col in new_cols.keys():
            if col not in df.columns: 
                df[col]=new_cols[col]['default']
                df[col]=df[col].astype(new_cols[col]['type'])
                            
        for i in range(len(date_ls)-1, -1, -1):
            dte = date_ls[i]
            _no_transactions = len(df[(df.date.dt.date == dte)]) 

            # if there's a first value for that day, work on from the first balance
            if True in df[(df.date.dt.date == dte)]['first'].values:
                first_i = 0
                last_i = _no_transactions
                for i in range(int(first_i)+1,int(last_i)):
                    comp_df = df[(df.date.dt.date == dte) & (df['order'] == float(i-1))].iloc[0]             
                    # has to use t_df instead of date_df to view the updated changes when i is assigned           
                    for index, row_dte in df[(df.date.dt.date == dte) & (df['order'].isna())].iterrows():
                        if i not in df[(df.date.dt.date == dte)]['order'].values:
                            if comp_df.balance == round(row_dte.balance-row_dte.amount,2):
                                df.loc[row_dte.name, 'order'] = i
                                if i == int(last_i)-1:
                                    df.loc[row_dte.name, 'last'] = True
            
            # if there's a last value for that day, work backwards from the End of day balance
            elif True in df[(df.date.dt.date == dte)]['last'].values:
                first_i = 0
                last_i = _no_transactions
                for i in range(int(last_i)-2,int(first_i)-1,-1):
                    comp_df = df[(df.date.dt.date == dte) & (df['order'] == float(i+1))].iloc[0]   
                    # has to use t_df instead of date_df to view the updated changes when i is assigned           
                    for index, row_dte in df[(df.date.dt.date == dte) & (df['order'].isna())].iterrows():
                        if i not in df[(df.date.dt.date == dte)]['order'].values:
                            if comp_df.balance == round(row_dte.balance-row_dte.amount,2):
                                df.loc[row_dte.name, 'order'] = i
                                if i == 0:
                                    df.loc[row_dte.name, 'first'] = True
        return df

    def _order_transactions(self, df:pd.DataFrame()=pd.DataFrame()) -> pd.DataFrame():
        """_summary_ REQUIRES df with field: date with dtype datetime64ns
        """        
        if df.empty:
            df = self._df

        df = self._find_first_and_last_transactions(df)
        df = self._order_middle_transactions(df)

        df.sort_values(by=['date','order'], inplace=True)
        df.drop(columns=['order','first','last'],inplace=True)
        df.reset_index(drop=True,inplace=True)
        return df