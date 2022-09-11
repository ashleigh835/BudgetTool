from common.config_info import Config

from datetime import datetime
import pandas as pd
import numpy as np
import os

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
    def __init__(self, df:pd.DataFrame()=pd.DataFrame(), hdf_path:str=None, provider:str=None) -> None:
        
        self.settings:dict = Config().settings()

        self._transactions:list = []
        self._hdf_path:str = hdf_path
        self._provider:str = provider

        self._df = self._load_df(df)

        pass

    def _load_transactions_from_drive(self) -> pd.DataFrame():
        if os.path.isfile(self._hdf_path):
            return pd.read_hdf(self._hdf_path, key='transactions', mode='r')
        else:
            return pd.DataFrame()

    def _load_df(self, df:pd.DataFrame()=pd.DataFrame()) -> pd.DataFrame():
        if not df.empty:
            return df
        elif self._hdf_path:
            return self._load_transactions_from_drive()

    @property
    def _most_recent_transaction(self) -> Transaction:
        if not self._df.empty:
            t = self._df[~self._df.balance.isna()]
            if not t.empty: return Transaction(**t.head(1).iloc[0].to_dict())

    @property
    def _most_recent_pending_transaction(self) -> Transaction:
        if not self._df.empty:
            t = self._df[self._df.balance.isna()]
            if not t.empty: return Transaction(**t.head(1).iloc[0].to_dict())
    
    def _determine_transaction_style(self) -> None:
        _class = None
        for cls in Transaction.__subclasses__():
            if self._provider in cls.supported_providers:
                _class = cls
        if _class is None:
            raise Exception(f"No supported transaction style for provider - contact development team")
        
        return _class
    
    def _load_transactions_from_csv(self, path:str=None, write:bool=True) -> None:
        if not path:
            print('please input the path of the file (including extension)')
            path = input('path: ')
            if not os.path.isfile(path):
                print('file not found.')
                return
        self._transaction_class_type = self._determine_transaction_style()
        df = pd.read_csv(path, index_col=False)
        for index, transaction_detail in df.iterrows():
            transaction = self._transaction_class_type(transaction_detail.to_dict())
            self._df = pd.concat([self._df, transaction._df_entry], axis=0)
            self._df.reset_index(drop=True, inplace=True)
        self._clean_transactions()
        if write: self._store_transactions_to_drive()
    
    def _load_individual_transaction(self, transaction_detail:dict, write:bool=True) -> None:
        self._transaction_class_type = self._determine_transaction_style()
        transaction = self._transaction_class_type(transaction_detail)
        self._df = pd.concat([self._df, transaction._df_entry], axis=0)
        if write: self._store_transactions_to_drive()

    def _load_transactions_from_folder(self, path:str=None, write:bool=True) -> None:
        path = path or self.settings['upload_folder']
        archive = self.settings['upload_archive'] + os.sep
        for entry in os.scandir(path):  
            self._load_transactions_from_csv(entry.path, write=False)
            os.system(f'move {entry.path} {archive}{os.path.basename(entry.path)}')
        if write: self._store_transactions_to_drive()

    def _clean_transactions(self) -> None:
        df = self._df
        df.drop_duplicates(inplace=True)
        # remove historical pending transactions
        df = df[~((df.balance.isna()) & (df.date.dt.date <= datetime.now().date()))]
        
        df.reset_index(drop=False, inplace=True)
        # if the csv balance is ordered with the most recent trasnaction at the top, it would need to be ascending=[False,True]
        df = df.sort_values(by=['date','index'], ascending=[False,False]).drop(columns='index').reset_index(drop=True)
        self._df = df

    def _store_transactions_to_drive(self) -> None:
        if not self._df.empty:
            self._df.to_hdf(self._hdf_path, key='transactions', mode='w', complevel=4, complib='zlib', encoding='UTF-8')

    def _project_transactions(self, existing_dates:int=5, scheduled_transactions_df:pd.DataFrame()=pd.DataFrame()) -> pd.DataFrame():
        last_5_dates_with_transactions = [date.date() for date in self._df.date.sort_values(ascending=True).drop_duplicates().tail(existing_dates)]
        existing_transactions_df = self._df[self._df.date.dt.date.isin(last_5_dates_with_transactions)].copy()
        
        # Faster to create a subclass of smaller subset of transactions and order those, instead of ordering all transactions
        existing_transactions_df = Transaction_Manager(df = existing_transactions_df)
        existing_transactions_df = existing_transactions_df._order_transactions()                

        df = pd.concat([existing_transactions_df, scheduled_transactions_df], axis=0)
        df.reset_index(drop=True,inplace=True)

        for i in range(len(existing_transactions_df), len(df)):
            df.loc[i, 'balance'] = df.loc[i-1, 'balance'] + df.loc[i,'amount']
        
        print(df)
        # ax = df.groupby('date',as_index=False).agg({'balance':'last'}).plot(x = 'date',y = 'balance')  
        # fig = ax.get_figure()
        # fig.savefig('test2.pdf')
        return df  

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