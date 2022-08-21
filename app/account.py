import pandas as pd

class Account(object):

    def __init__(self, account_holder, account_name, account_type) -> None:
        self._account_holder = account_holder
        self._account_name = account_name
        self._account_type = account_type
        self._provider = self._determine_provider()
        pass
