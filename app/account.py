from app.transaction import Transaction

from common.mapping import Mapping

from helpers.class_integrators import parse_supported_providers

import pandas as pd

class Account(object):

    def __init__(self, account_holder, account_name, account_type=None, account_provider=None) -> None:
        self._account_type_map = Mapping()._account_type

        self._account_holder = account_holder
        self._account_name = account_name

        if account_type is None: 
            self._account_type = self._determine_account_type(account_type)
        else: self._account_type = account_type

        if account_provider is None: 
            self._account_provider = self._determine_provider(account_provider)
        else: self._account_provider = account_provider

        self._config = self._create_config()
        pass

    def _create_config(self) -> dict:
        return {
            self._account_holder : [{
                'account_name' : self._account_name ,
                'account_type' : self._account_type,
                'account_provider' : self._account_provider
            }]
        }

    def _determine_account_type(self, account_type=None) -> str :        
        if account_type is None: account_type = input('Account Type C/S/I (Checking/Savings/Investment): ')
        while account_type.upper() not in ['C','S','I']:
            print('please enter one of the following: C/S/I (Checking/Savings/Investment).')
            account_type = input('C/S/I: ')
        return self._account_type_map[account_type.upper()]

    def _determine_provider(self, _account_provider=None) -> str:
        supported_providers_dict = parse_supported_providers(Transaction)
        print('Choose a provider. Use the number listed below to choose your option')
        for indx in supported_providers_dict.keys(): print(f'{indx}: {supported_providers_dict[indx]}')
        provider_choose_input = input('please enter an index from above: ')
        while provider_choose_input.lower() not in [str(indx) for indx in supported_providers_dict.keys()]:
            provider_choose_input = input(f'please enter an index from above: ')        
        return supported_providers_dict[int(provider_choose_input)]

    def _determine_transaction_style(self) -> None:
        _class = None
        for cls in Transaction.__subclasses__():
            if self._account_provider in cls.supported_providers:
                _class = cls
        if _class is None:
            raise Exception(f"No supported transaction style for provider - contact development team")
        
        return _class
    
    def _load_transactions_from_csv(self, transaction_detail) -> pd.DataFrame():
        class_type = self._determine_transaction_style()
        t = class_type(transaction_detail)
        return t
        # 

    # def _store_transactions(self, transaction_detail) -> dict:
    #     t = T(**transaction_detail)
    #     return {}
    
    # def _import_from_csv(self, path) -> pd.DataFrame():
    #     # return pd.read_csv(self._path, index_col=False)
    #     return pd.read_csv(path, index_col=False)