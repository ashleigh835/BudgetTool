from helpers.input_helpers import determine_from_ls, determine_amount, determine_weekday, determine_day_of_month, determine_date, determine_from_range

class Scheduled_Transaction(object):
    _type:str = None
    _amount:float = None
    _frequency:str = None
    _frequency_timing:object = None
    _summary:str = None
    _description:str = None

    def __init__(self, t_summary:str=None, t_type:str=None, t_amount:float=None, t_freq:str=None, t_freq_timing=None, t_desc:str=None) -> None:
        if not t_summary: self._summary = self._determine_summary()
        if not t_desc: self._description = self._determine_description()
        if not t_type: self._type = self._determine_scheduled_transaction_type()
        if not t_amount: self._amount = self._determine_amount()
        if not t_freq: self._frequency = self._determine_frequency()
        if not t_freq_timing: self._frequency_timing = self._determine_frequency_timing()
        pass

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