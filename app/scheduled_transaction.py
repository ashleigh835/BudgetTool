from app.helpers.input_helpers import determine_from_ls, determine_amount, determine_weekday, determine_day_of_month, determine_date, determine_from_range, input_yn
import itertools

class Scheduled_Transaction(object):
    _index = itertools.count()

    def __init__(self, _summary:str=None, _type:str=None, _amount:float=None, _frequency:dict={}, _description:str=None, new:bool=False) -> None:
        self._summary:str = None
        self._description:str = None
        self._type:str = None
        self._amount:float = None
        self._frequency:dict = {}

        self._index = next(self._index)
        self._summary = _summary or self._determine_summary()
        if new: 
            self._description = _description or self._determine_description()
        else:
            self._description = _description
        self._type = _type or self._determine_scheduled_transaction_type()
        self._amount = _amount or self._determine_amount()
        self._frequency = _frequency or self._determine_frequency()
        pass

    @property
    def _config(self):
        return {
            '_summary' : self._summary,
            '_description' : self._description,
            '_type' : self._type,
            '_amount' : self._amount,
            '_frequency' :self._frequency
        }

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
    
    def _determine_frequency(self) -> dict:
        finished = False
        while not finished:
            _frequency = determine_from_ls(['one-off', 'daily','weekly','monthly','yearly','custom interval'])
            _frequency, _frequency_timing = self._determine_frequency_timing(_frequency)
            self._update_frequency(_frequency, _frequency_timing)
            print('Add another frequency rule for this scheduled transaction?')
            choose = input_yn()
            if choose == 'N':
                finished = True
        return self._frequency

    def _determine_frequency_timing(self, _frequency:str):
        if _frequency == 'one-off':
           return _frequency, determine_date()
        elif _frequency == 'weekly':            
            return _frequency, determine_weekday()
        elif _frequency == 'monthly':           
            return _frequency, determine_day_of_month(['End'])
        elif _frequency == 'yearly':
            return _frequency, determine_date()
        elif _frequency == 'custom interval':
            recursion_str = 're-select frequency'
            ft = determine_from_range(1,365,[recursion_str],string='an interval (in days)')
            if ft == recursion_str: 
                print('please re-select your frequency')
                _frequency = self._determine_frequency()
                return self._determine_frequency_timing()
            else:
                return _frequency, ft
    
    def _update_frequency(self, _frequency:str, _frequency_timing:object) -> None:
        if _frequency not in self._frequency.keys():        
            self._frequency[_frequency] = [_frequency_timing]
        else:
            if _frequency_timing not in self._frequency[_frequency]:
                self._frequency[_frequency]+=[_frequency_timing]
    
    def _remove_frequency(self, _frequency:str, _frequency_timing:object) -> None:
        if _frequency in self._frequency.keys():
            if _frequency_timing in self._frequency[_frequency]:
                self._frequency[_frequency].remove(_frequency_timing)
                if not self._frequency[_frequency]:
                    del self._frequency[_frequency]
