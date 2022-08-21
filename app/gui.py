from common.config_info import Config

from app.account import Account

from helpers.input_helpers import input_yn

import json
import os

class GUI(object):
    _accounts = []

    def __init__(self) -> None:
        self.settings = Config().settings()
        
        self._account_config_path = self.settings['account_config']
        self._account_config = self._determine_config()
        print(self._account_config)

        self._user_dict = self._parse_users()
        self._users = self._list_users()

        self._account_dict = self._parse_accounts()
        self._accounts = self._list_accounts()
        self._account_nicknames = self._list_account_nicknames()
        pass

    def __reset__(self) -> None:
        self.__init__()

    def _determine_config(self) -> None:
        if not os.path.isfile(self._account_config_path):
            print('no config found, initializing setup...')
            return self._setup()
        else:
            return self._load_config()

    def _setup(self) -> None:
        config = self._create_account_dict()
        self._create_config(config)
        self.__reset__()

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
        self.__reset__()

    def _create_config(self, config) -> dict:
        json_obj = json.dumps(config, indent=4)
        with open(self._account_config_path,"w") as of:
            of.write(json_obj)
        return config

    def _load_config(self) -> dict:
        with open(self._account_config_path,'r') as of:
            json_obj = json.load(of)
        return json_obj

    def _rewrite_config(self, config) -> dict:
        self._create_config(config)
        return config
    
    def _append_new_account_to_config(self, account) -> dict:
        config = self._account_config
        for account_holder in account.keys():
            if account_holder in config: 
                config[account_holder] += account[account_holder]
            else:
                config[account_holder] = account[account_holder]
        return self._rewrite_config(config)

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
        return [self._account_dict[account]._account_name for account in self._account_dict.keys()]

