from common.config_info import Config

from app.account import Account_Manager

from helpers.input_helpers import determine_from_ls, view_readable, determine_operation_from_dict

import json
import os

class GUI(object):
    def __init__(self) -> None:
        self.settings = Config().settings()
        self._account_config_path = self.settings['account_config']
        self._account_config = self._determine_config()
        print('**'*20)
        print(self._account_config)
        print('**'*20)

        self._Account_Manager = self._load_accounts()

        self._load_options()

        if self._check_save(): self._save()
        pass

        # Need an async function to ensure the account_config file always matches account_config
    
    def __setattr__(self, __name, __value) -> None:
        self.__dict__[__name] = __value
        pass

    def __reset__(self) -> None:
        self.__init__()
    
    def _check_save(self) -> bool:
        if self._account_config != self._Account_Manager._config: 
            print('***'*20)
            print(self._account_config)
            print('---'*20)
            print(self._Account_Manager._config)
            print('***'*20)
            return True

    def _save(self) -> None:
        self._rewrite_config(self._Account_Manager._config)

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

    def _add_account(self) -> None:
        self._Account_Manager._add_account()
        self._rewrite_config(self._Account_Manager._config)

    def _choose_account(self): # -> Account:
        print()
        account = determine_from_ls(self._Account_Manager._accounts, string='an account', labels=self._Account_Manager._account_nicknames)
        return account

    def _manage_account(self) -> None:
        account = self._choose_account()
        operations = {
            # 'delete account' : self._add_account,
            'view all account details' : {'function' : view_readable, 'vars' : {'read_item' : account._config[account._holder][0]}},
            'view scheduled transactions' : {
                'function' : view_readable, 
                'vars' : {
                    'name':'scheduled_transactions', 
                    'read_item':account._config[account._holder][0]['scheduled_transactions']
                }
            },
            'add scheduled transactions' : {'function' : account._add_scheduled_transaction, 'vars' : None},
            'add transactions from a path' : {'function' : account._load_transactions_from_csv, 'vars' : None},
            'import all csvs in upload folder' : {'function' : account._load_transactions_from_folder, 'vars' : None},
            'Exit' : {'function' : 'Exit',}
        }
        determine_operation_from_dict(operations)
                    
    def _load_options(self) -> None:
        operations = {
            'Add a new account' : {'function' : self._add_account,'vars' : None},
            'Manage account' : {'function' : self._manage_account,'vars' : None},
            'Exit' : {'function' : 'Exit'}
        }
        determine_operation_from_dict(operations)



