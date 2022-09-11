from datetime import date, timedelta

def weekdays():
    return[date(2022,8,i).strftime('%A') for i in range(1,8)]

def last_day_of_month(date:date):
    if date.month == 12:
        return date.replace(day=31)
    else:
        return date.replace(month=date.month+1,day=1) + timedelta(days=-1)        
    
def days_matching_within_range(start_date:date, days_range:int, days:list) -> list:
    _date_range = [start_date + timedelta(days=d) for d in range(0,days_range)]
    _date_ls = []
    _date_ls += [date for date in _date_range if str(date.day) in days]
    if 'End' in days:
        _date_ls += [date for date in _date_range if date==last_day_of_month(date)]
    return _date_ls
    
