import os
class Config:
    def __init__(self) -> None:
        self._settings = {
            'account_config' : 'account_config.json',
            'account_types' : ['Checking','Savings','Investments'],
            'upload_folder' : os.getcwd() + os.sep + 'data' + os.sep + 'upload',
            'upload_archive' : os.getcwd() + os.sep + 'data' + os.sep + 'upload_archive',
            'transaction_folder' : os.getcwd() + os.sep + 'data' + os.sep + 'transactions',
            'assets' : os.getcwd() + os.sep + 'assets'
        }
        pass

    def settings(self) -> dict:
        return self._settings