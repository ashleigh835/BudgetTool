import datetime

def weekdays():
    return[datetime.date(2022,8,i).strftime('%A') for i in range(1,8)]
    
