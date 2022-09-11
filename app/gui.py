from common.config_info import Config

from app.account import Account_Manager

from helpers.input_helpers import view_readable, determine_operation_from_dict

import json
import os

class GUI(object):
    def __init__(self) -> None:
        self.settings = Config().settings()
        self._account_config_path = self.settings['account_config']
        self._account_config = self._determine_config()

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

    def _manage_account(self) -> None:
        """_summary_ Offer options to manage account.
        """        
        account = self._Account_Manager._choose_account()
        # Loop from outside of the function so that any changes to self will be reloaded into the operations dict and pass through to the determine function
        reload_self = True
        while reload_self:
            operations = {
                'Delete account' : {'function' : self._Account_Manager._delete_account, 'vars' : {'account' : account}},
                'Ammend details' : {'function' : self._Account_Manager._ammend_account, 'vars' : {'account' : account}},
                'Ammend scheduled transactions' : {'function' : self._Account_Manager._ammend_scheduled_transactions, 'vars' : {'account' : account}},
                'View all account details' : {'function' : view_readable, 'vars' : {'read_item' : account._config[account._holder][0]}},
                'View scheduled transactions' : {
                    'function' : view_readable, 
                    'vars' : {
                        'name':'scheduled_transactions', 
                        'read_item':account._config[account._holder][0]['scheduled_transactions']
                    }
                },
                'View date of most recent transaction' : {'function' : account._view_most_recent_transaction_date, 'vars' : None},
                'Add scheduled transactions' : {'function' : account._add_scheduled_transaction, 'vars' : None},
                'Add transactions from a path' : {'function' : account._load_transactions_from_csv, 'vars' : None},
                'Import all csvs in upload folder' : {'function' : account._load_transactions_from_folder, 'vars' : None},
                'Project Transactions' : {'function' : account._project_transactions, 'vars' : None},
                'Exit' : {'exit' : ''}
            }
            reload_self = determine_operation_from_dict(operations, refresh_dict=True)
                    
    def _load_options(self) -> None:
        """_summary_ offer initial gui options
        """        
        # Loop from outside of the function so that any changes to self will be reloaded into the operations dict and pass through to the determine function
        reload_self = True
        while reload_self:
            operations = {
                'Add a new account' : {'function' : self._add_account,'vars' : None},
                'Delete an existing account' : {'function' : self._Account_Manager._delete_account, 'vars' : None},
                'Manage an existing account' : {'function' : self._manage_account,'vars' : None},
                'Exit' : {'exit' : ''}
            }
            reload_self = determine_operation_from_dict(operations)



