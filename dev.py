from app.account import Account

import os

for entry in os.scandir('.\data'):       
    account = Account(entry)
    df = account._df
    print(df.tail())