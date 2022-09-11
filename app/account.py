from app.transaction import Transaction, Transaction_Manager
from app.scheduled_transaction import Scheduled_Transaction

from helpers.input_helpers import input_yn, determine_from_ls, enum_ls, view_readable
from helpers.date_helpers import days_matching_within_range

from common.config_info import Config

from datetime import datetime, timedelta
import os
import pandas as pd
import numpy as np

class Account(object):
    def __init__(self, account_holder:str, account_name:str, account_type:str=None, account_provider:str=None, scheduled_transactions:list=[]) -> None:
        self._holder = None
        self._name = None
        # self._type = None
        # self._provider = None

        self._scheduled_transactions = []

        self.settings = Config().settings()
        
        self._holder = account_holder
        self._name = account_name
        self._type = account_type or self._determine_account_type()
        self._provider = account_provider or self._determine_provider()

        if scheduled_transactions:
            self._scheduled_transactions += self.get_scheduled_transactions_from_config(scheduled_transactions)

        self._transaction_df = self._load_transactions_from_drive()
        pass
    
    @property
    def _config(self):
        return {
            self._holder : [{
                'account_name' : self._name ,
                'account_type' : self._type,
                'account_provider' : self._provider,
                'scheduled_transactions' : self._scheduled_transaction_config
            }]
        }

    @property
    def _scheduled_transaction_config(self) -> list:
        _config = []
        for scheduled_transaction in self._scheduled_transactions:
            _config += [scheduled_transaction._config]
        return _config
    
    @property
    def _scheduled_transaction_summary(self) -> list:
        return [st._summary for st in self._scheduled_transactions]

    @property
    def _transaction_hdf(self) -> str:
        return f"{self.settings['transaction_folder']}{os.sep}{self._holder}_{self._name}_transactions.h5"

    @property
    def _most_recent_transaction(self) -> Transaction:
        if not self._transaction_df.empty:
            t = self._transaction_df[~self._transaction_df.balance.isna()]
            if not t.empty: return Transaction(**t.head(1).iloc[0].to_dict())

    @property
    def _most_recent_pending_transaction(self) -> Transaction:
        if not self._transaction_df.empty:
            t = self._transaction_df[self._transaction_df.balance.isna()]
            if not t.empty: return Transaction(**t.head(1).iloc[0].to_dict())

    def get_scheduled_transactions_from_config(self, _config:dict=None) -> list:
        scheduled_transactions = []
        _config = _config or self._scheduled_transaction_config
        for scheduled_transaction in _config:
            temp_scheduled_transactions = Scheduled_Transaction(**scheduled_transaction)
            scheduled_transactions += [temp_scheduled_transactions]
        return scheduled_transactions

    def _determine_account_type(self) -> str :
        return determine_from_ls(self.settings['account_types'], string='a provider')

    def _determine_provider(self) -> str:
        return determine_from_ls(Transaction._supported_providers, 'a provider')

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
            self._transaction_df = pd.concat([self._transaction_df, transaction._df_entry], axis=0)
            self._transaction_df.reset_index(drop=True, inplace=True)
        self._clean_transactions()
        if write: self._store_transactions_to_drive()
    
    def _load_individual_transaction(self, transaction_detail:dict, write:bool=True) -> None:
        self._transaction_class_type = self._determine_transaction_style()
        transaction = self._transaction_class_type(transaction_detail)
        self._transaction_df = pd.concat([self._transaction_df, transaction._df_entry], axis=0)
        if write: self._store_transactions_to_drive()

    def _load_transactions_from_folder(self, path:str=None, write:bool=True) -> None:
        path = path or self.settings['upload_folder']
        archive = self.settings['upload_archive'] + os.sep
        for entry in os.scandir(path):  
            self._load_transactions_from_csv(entry.path, write=False)
            os.system(f'move {entry.path} {archive}{os.path.basename(entry.path)}')
        if write: self._store_transactions_to_drive()

    def _clean_transactions(self) -> None:
        df = self._transaction_df
        df.drop_duplicates(inplace=True)
        # remove historical pending transactions
        df = df[~((df.balance.isna()) & (df.date.dt.date <= datetime.now().date()))]
        
        df.reset_index(drop=False, inplace=True)
        # if the csv balance is ordered with the most recent trasnaction at the top, it would need to be ascending=[False,True]
        df = df.sort_values(by=['date','index'], ascending=[False,False]).drop(columns='index').reset_index(drop=True)
        self._transaction_df = df

    def _load_transactions_from_drive(self) -> pd.DataFrame():
        if os.path.isfile(self._transaction_hdf):
            return pd.read_hdf(self._transaction_hdf, key='transactions', mode='r')
        else:
            return pd.DataFrame()

    def _store_transactions_to_drive(self) -> None:
        if not self._transaction_df.empty:
            self._transaction_df.to_hdf(self._transaction_hdf, key='transactions', mode='w', complevel=4, complib='zlib', encoding='UTF-8')

    def _get_most_recent_transaction_date(self) -> datetime.date:
        return self._most_recent_transaction._date.date()

    def _view_most_recent_transaction_date(self) -> dict:
        print(self._get_most_recent_transaction_date())

    def _add_scheduled_transaction(self) -> None:        
        self._scheduled_transactions += [self._get_scheduled_transaction_from_user()]
    
    def _create_scheduled_transaction(self, t_summary:str=None, t_type:str=None, t_amount:float=None, t_freq:str=None, t_desc:str=None, new:bool=True) -> Scheduled_Transaction:
        return Scheduled_Transaction(t_summary, t_type, t_amount, t_freq, t_desc, new)

    def _get_scheduled_transaction_from_user(self) -> Scheduled_Transaction:     
        return self._create_scheduled_transaction(new=True)

    def _project_transactions(self, days:int=45) -> pd.DataFrame():
        _start_date = self._get_most_recent_transaction_date()
        last_5_dates_with_transactions = [date.date() for date in self._transaction_df.date.sort_values(ascending=True).drop_duplicates().tail(5)]
        t_df = self._transaction_df[self._transaction_df.date.dt.date.isin(last_5_dates_with_transactions)].copy()
        st_df = pd.DataFrame()
        for st in self._scheduled_transactions:            
            for rule in st._config['_frequency'].keys():
                if rule == 'monthly':
                    for date in days_matching_within_range(_start_date, days, st._config['_frequency']['monthly']):
                        multiplier = 1
                        if st._type == 'DEBIT': multiplier = -1
                        t_detail = {
                            'type' : st._type ,
                            'date' : date,
                            'description' : st._summary ,
                            'amount' : st._amount * multiplier,
                            'payment_type' : '' ,
                            'balance' : np.nan,
                            'scheduled' : True,
                            'forecasted' : True
                        }
                        t = Transaction(**t_detail)
                        st_df = pd.concat([st_df,t._df_entry], axis=0)
                else:
                    print(f'{rule} frequency not yet supported for projection')
        
        projected_transactions = Transaction_Manager(t_df)
        t_df = projected_transactions._order_transactions()        
        
        st_df.sort_values(by='date', inplace=True)

        df = pd.concat([t_df, st_df], axis=0)
        df.reset_index(drop=True,inplace=True)

        for i in range(len(t_df), len(df)):
            df.loc[i, 'balance'] = df.loc[i-1, 'balance'] + df.loc[i,'amount']
        
        print(df)
        # ax = df.groupby('date',as_index=False).agg({'balance':'last'}).plot(x = 'date',y = 'balance')  
        # fig = ax.get_figure()
        # fig.savefig('test2.pdf')
        return df  

class Account_Manager(object):
    _accounts=[]

    def __init__(self, _config={}) -> None:

        if not _config:
            print('no config found, initializing setup...')
            account = self._create_account()
            if not account: 
                print('setup cancelled')
                return
            _config = account._config

        self._accounts += self._get_accounts_from_config(_config)
        pass

    @property
    def _config(self) -> dict:
        _config = {}
        for account in self._accounts:
            if account._holder in _config.keys(): 
                _config[account._holder] += account._config[account._holder]
            else:
                _config[account._holder] = account._config[account._holder]
        return _config

    @property
    def _user_dict(self) -> dict:
        return enum_ls(set([account._holder for account in self._accounts]))   

    @property
    def _users(self) -> list:
        return list(self._user_dict.values())

    @property
    def _account_nicknames(self) -> list:
        return [account._name for account in self._accounts]

    def _get_accounts_from_config(self, _config:dict=None) -> list:
        """Create account classes and load to a list. Loads from self._config unless a config is provided

        Args:
            _config (dict, optional): see account._config description. Defaults to None.

        Returns:
            list: list of Accounts (class objects)
        """                
        accounts = []
        _config = _config or self._config
        for _holder in _config.keys():
            for account_config in _config[_holder]:
                account = Account(_holder, **account_config)
                accounts += [account]
        return accounts

    def _determine_nickname(self, confirm_nickname:bool=False) -> None:
        account_name = input('Account Nickname: ')
        if confirm_nickname:
            while account_name in self._account_nicknames:
                print(f'That nickname already exist, choose something else (or C to cancel): ')
                account_name = input('Account Nickname: ')      
            if account_name.lower() == 'c': return 
        return account_name

    def _determine_user(self, confirm_user:bool=False) -> None:
        account_holder = input('Account Holder: ')
        if confirm_user:
            if account_holder not in self._users:
                print(f'That user did not already exist, add new user: {account_holder}?')
                if input_yn() == 'N': account_holder = self._determine_existing_user()
        return account_holder

    def _determine_existing_user(self) -> None:
        print('Which account holder did you mean? Use the number listed below to choose your option')
        for indx in self._user_dict.keys(): print(f'{indx}: {self._user_dict[indx]}')
        print('C: Cancel')
        account_user_choose_input = input('please enter an index from above or C to cancel: ')
        while account_user_choose_input.lower() not in [str(indx) for indx in self._user_dict.keys()]+['c']:
            account_user_choose_input = input(f'please enter an index from above or C to cancel: ')        
        if account_user_choose_input.lower() !='c': return self._user_dict[int(account_user_choose_input)]

    def _store_all_transactions(self) -> None:
        for account in self._accounts:
            account._store_transactions_to_drive()

    def _add_account(self) -> None:        
        self._accounts += [self._create_account(confirm_user=True)]

    def _delete_account(self, account:Account=None) -> None:
        if not account:
            account = self._choose_account()
        if account in self._accounts:
            account_name = account._name
            account_holder = account._holder
            print(f'Are you sure you want to delete account {account._name} (holder:{account_holder})')
            sure = input_yn()
            if sure == 'Y': 
                self._accounts.remove(account)
                print(f'account: {account_name} removed.')

    def _choose_account(self) -> Account:
        print()
        account = determine_from_ls(self._accounts, string='an account', labels=self._account_nicknames)
        return account

    def _create_account(self, confirm_user:bool=False) -> Account:
        print('Please provide information below')
        account_name = self._determine_nickname()
        if not account_name: return

        account_holder = self._determine_user(confirm_user)
        if not account_holder: return
        
        return Account(account_holder, account_name)
    
    def _ammend_account(self, account:Account) -> None:
        if not account:
            account = self._choose_account()
        var = determine_from_ls(['account_holder', 'account_name', 'account_type', 'account_provider'])
        if var == 'account_holder':
            account._holder = self._determine_user(True)
        elif var == 'account_name':
            account._name = self._determine_nickname(True)
        elif var == 'account_type':
            account._type = account._determine_account_type()
        elif var == 'account_provider':
            account._provider = account._determine_provider()
    
    def _ammend_scheduled_transactions(self, account:Account) -> None:        
        st = determine_from_ls(account._scheduled_transactions, string='an account', labels=account._scheduled_transaction_summary)
        
        print(st._config)
        view_readable(st._config)

        var = determine_from_ls(st._config.keys())
        if var == '_amount':
            st._amount = st._determine_amount()