from helpers.input_helpers import determine_from_ls, determine_amount, determine_weekday, determine_day_of_month

class Scheduled_Transaction(object):

    def __init__(self, t_type=None, t_amount=None, t_freq=None, t_freq_timing=None, t_summary=None, t_desc=None) -> None:
        if not t_type: 
            self._type = self._determine_scheduled_transaction_type()
        else:
            self._type = t_type
        
        if not t_amount: 
            self._amount = self._determine_amount()
        else:
            self._amount = t_amount
        
        if not t_freq: 
            self._frequency = self._determine_frequency()
        else:
            self._frequency = t_freq

        if not t_freq_timing: 
            self._frequency_timing = self._determine_frequency_timing()
        else:
            self._frequency_timing = t_freq_timing

        self._summary = 'a'
        self._desc = 'a1'
        # _date = input() # range(0-31, 'END')
        # _desc = input()

        # self._df_entry =  self._create_df_entry()
        pass

    def _determine_scheduled_transaction_type(self):   
        return determine_from_ls(['DEBIT', 'CREDIT'], string='whether this will be incoming or outgoing,', labels=['outgoing transaction','incoming payment'])

    def _determine_amount(self):
        return determine_amount('payment amount')
    
    def _determine_frequency(self):
        return determine_from_ls(['one-off', 'daily','weekly','monthly','quarterly','yearly'])

    def _determine_frequency_timing(self):
        if self._frequency == 'one-off':
            print('when tho: DATE')
        elif self._frequency == 'weekly':            
            self._frequency_timing = determine_weekday()
        elif self._frequency == 'monthly':           
            self._frequency_timing = determine_day_of_month(['End'])
        elif self._frequency == 'quarterly':        
            print('when tho: DAY OF QUARTER')
        elif self._frequency == 'yearly':
            print('when tho: DATE')