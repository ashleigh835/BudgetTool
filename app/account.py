from app.transaction import Transaction
from app.scheduled_transaction import Scheduled_Transaction

from helpers.input_helpers import input_yn, determine_from_ls

from common.config_info import Config

import pandas as pd

class Account(object):
    _type = None
    _provider = None

    def __init__(self, account_holder, account_name, account_type=None, account_provider=None) -> None:
        self.settings = Config().settings()

        self._holder = account_holder
        self._name = account_name

        if not account_type: self._type = self._determine_account_type(account_type)
        if not account_provider: self._provider = self._determine_provider(account_provider)

        self._config = self._create_config()

        self._transaction_df = pd.DataFrame()
        pass

    def _create_config(self) -> dict:
        return {
            self._holder : [{
                'account_name' : self._name ,
                'account_type' : self._type,
                'account_provider' : self._provider
            }]
        }

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
    
    def _load_transactions_from_csv(self, path) -> pd.DataFrame():
        self._transaction_class_type = self._determine_transaction_style()
        df = self._import_from_csv(path) 
        for index, transaction_detail in df.iterrows():
            transaction = self._transaction_class_type(transaction_detail.to_dict())
            self._transaction_df = pd.concat([self._transaction_df, transaction._df_entry], axis=0)
    
    def _load_individual_transaction(self, transaction_detail):
        self._transaction_class_type = self._determine_transaction_style()
        transaction = self._transaction_class_type(transaction_detail)
        self._transaction_df = pd.concat([self._transaction_df, transaction._df_entry], axis=0)
    
    def _add_scheduled_transaction(self):
        return 

    def _get_scheduled_transaction_from_user(self):     
        return Scheduled_Transaction()

    def _import_from_csv(self, path) -> pd.DataFrame():
        return pd.read_csv(path, index_col=False)

class Account_Manager(object):

    def __init__(self, account_config={}) -> None:

        if account_config == {}:
            print('no config found, initializing setup...')
            account_config = self._create_account_dict()

        self._account_config = account_config

        self._user_dict = self._parse_users()
        self._users = self._list_users()

        self._account_dict = self._parse_accounts()
        self._accounts = self._list_accounts()
        self._account_nicknames = self._list_account_nicknames()
        pass

    def _parse_users(self) -> list:
        return dict((i,j) for i,j in enumerate(self._account_config.keys()))      

    def _list_users(self) -> list:
        return [self._user_dict[user] for user in self._user_dict.keys()]   
    
    def _parse_accounts(self) -> list:
        accounts = []
        for account_holder in self._users:
            for account_config in self._account_config[account_holder]:
                account = Account(account_holder, **account_config)
                accounts += [account]
        return dict((i,j) for i,j in enumerate(accounts))

    def _list_accounts(self) -> list:
        return [self._account_dict[account] for account in self._account_dict.keys()]

    def _list_account_nicknames(self) -> list:
        return [self._account_dict[account]._name for account in self._account_dict.keys()]

    def _create_account_dict(self, confirm_user=False) -> dict:
        print('Please provide information below')
        account_name = self._determine_nickname()
        if account_name == None:
            return

        account_holder = self._determine_user(confirm_user)
        if account_holder == None:
            return
        
        account = Account(account_holder, account_name)
        return account._config

    def _determine_nickname(self, confirm_nickname=False) -> None:
        account_name = input('Account Nickname: ')
        if confirm_nickname:
            while account_name in self._account_nicknames:
                print(f'That nickname already exist, choose something else (or C to cancel): ')
                account_name = input('Account Nickname: ')      
            if account_name.lower() == 'c': return 
        return account_name

    def _determine_user(self, confirm_user=False) -> None:
        account_holder = input('Account Holder: ')
        if confirm_user:
            if account_holder not in self._users:
                print(f'That user did not already exist, add new user: {account_holder}?')
                if input_yn() == 'N': account_holder = self._determine_existing_user()
        return account_holder

    def _determine_existing_user(self, account_holder=None) -> None:
        print('Which account holder did you mean? Use the number listed below to choose your option')
        for indx in self._user_dict.keys(): print(f'{indx}: {self._user_dict[indx]}')
        print('C: Cancel')
        account_user_choose_input = input('please enter an index from above or C to cancel: ')
        while account_user_choose_input.lower() not in [str(indx) for indx in self._user_dict.keys()]+['c']:
            account_user_choose_input = input(f'please enter an index from above or C to cancel: ')        
        if account_user_choose_input.lower() !='c': return self._user_dict[int(account_user_choose_input)]

    def _add_account(self) -> None:
        config = self._create_account_dict(confirm_user=True)
        self._append_new_account_to_config(config)

    def _append_new_account_to_config(self, account) -> dict:
        config = self._account_config
        for account_holder in account.keys():
            if account_holder in config: 
                config[account_holder] += account[account_holder]
            else:
                config[account_holder] = account[account_holder]
        self._account_config = config
        return self._account_config