import os

from app.gui import GUI

gui = GUI()

account = gui._accounts[0]

for entry in os.scandir('.\data'):  
    account._load_transactions_from_csv(entry.path)

print(account._transaction_df)