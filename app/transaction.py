import pandas as pd

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
