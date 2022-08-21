from datetime import date
import pandas as pd

class Transaction(object):
    _supported_providers = []

    def __init__(self, t_amount, t_type, t_date, t_description, t_payment_type, t_balance) -> None:
        self._amount = t_amount
        self._type = t_type
        self._date = t_date
        self._description = t_description
        self._payment_type = t_payment_type
        self._balance = t_balance
        pass

    def __init_subclass__(cls) -> None:
        cls._supported_providers += cls.supported_providers
        pass

    def _translate(self, kwargs) -> None:
        for transaction_arg in self.mapping:
            for arg in kwargs:
                if arg == self.mapping[transaction_arg]: 
                    self.conversion_dict[transaction_arg] = kwargs[arg]
        
        return super(self.__class__, self).__init__(**self.conversion_dict)        

class Trasaction_Type_1(Transaction):
    supported_providers = ['Chase']
    mapping = { 
        't_type' : 'Details' ,
        't_date' : 'Posting Date' ,
        't_description' : 'Description' ,
        't_amount' : 'Amount' ,
        't_payment_type' : 'Type' ,
        't_balance' : 'Balance' 
    }
    conversion_dict = {}

    def __init__(self, kwargs) -> None:        
        return self._translate(kwargs)
        
class Trasaction_Type_2(Transaction):
    supported_providers = ['Lloyds']
    mapping = { 
        't_type' : 'Details' ,
        't_date' : 'Posting Date' ,
        't_description' : 'Description' ,
        't_amount' : 'Amount' ,
        't_payment_type' : 'Type' ,
        't_balance' : 'Bal' 
    }
    conversion_dict = {}

    def __init__(self, kwargs) -> None:       
        return self._translate(kwargs)
