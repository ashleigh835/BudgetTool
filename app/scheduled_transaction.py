from helpers.input_helpers import determine_from_ls, determine_amount, determine_weekday, determine_day_of_month, determine_date, determine_from_range

class Scheduled_Transaction(object):
    _summary:str = None
    _description:str = None
    _type:str = None
    _amount:float = None
    _frequency:str = None
    _frequency_timing:object = None

    def __init__(self, _summary:str=None, _type:str=None, _amount:float=None, _frequency:str=None, _frequency_timing=None, _description:str=None, new:bool=False) -> None:
        self._summary = _summary or self._determine_summary()
        if new: 
            self._description = _description or self._determine_description()
        else:
            self._description = _description
        self._type = _type or self._determine_scheduled_transaction_type()
        self._amount = _amount or self._determine_amount()
        self._frequency = _frequency or self._determine_frequency()
        self._frequency_timing = _frequency_timing or self._determine_frequency_timing()
        pass

    @property
    def _config(self):
        return self.__dict__

    def _determine_summary(self):
        print('in as few words as possible, what is the nickname for this transaction?')
        return input('Summary: ')

    def _determine_description(self):
        print('Would you like to add more information about this transaction for your own reference? (Leave blank if not)')
        return input('Description: ')

    def _determine_scheduled_transaction_type(self):   
        return determine_from_ls(['DEBIT', 'CREDIT'], string='whether this will be incoming or outgoing,', labels=['outgoing transaction','incoming payment'])

    def _determine_amount(self):
        return determine_amount('payment amount')
    
    def _determine_frequency(self):
        return determine_from_ls(['one-off', 'daily','weekly','monthly','yearly','custom interval'])

    def _determine_frequency_timing(self):
        if self._frequency == 'one-off':
           return determine_date()
        elif self._frequency == 'weekly':            
            return determine_weekday()
        elif self._frequency == 'monthly':           
            return determine_day_of_month(['End'])
        elif self._frequency == 'yearly':
            return determine_date()
        elif self._frequency == 'custom interval':
            recursion_str = 're-select frequency'
            ft = determine_from_range(1,365,[recursion_str],string='an interval (in days)')
            if ft == recursion_str: 
                print('please re-select your frequency')
                self._frequency = self._determine_frequency()
                return self._determine_frequency_timing()
            else:
                return ft