from common.config_info import Config

from app.account import Account_Manager

import json
import os

class GUI(object):
    _accounts = []

    def __init__(self) -> None:
        self.settings = Config().settings()
        self._account_config_path = self.settings['account_config']
        self._account_config = self._determine_config()
        print(self._account_config)

        self._Account_Manager = self._load_accounts()

        if self._account_config != self._Account_Manager._account_config:
            self._rewrite_config(self._Account_Manager._account_config)
        pass

        # Need an async function to ensure the account_config file always matches account_config
    
    def __setattr__(self, __name, __value) -> None:
        self.__dict__[__name] = __value
        pass

    def __reset__(self) -> None:
        self.__init__()

    def _determine_config(self) -> dict:
        if os.path.isfile(self._account_config_path):
            return self._load_config()
        else:
            return {}

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
        self.__reset__()
    
    def _load_accounts(self):
        return Account_Manager(self._account_config)

    def _add_account(self):
        self._Account_Manager._add_account()
        self._rewrite_config(self._Account_Manager._account_config)



