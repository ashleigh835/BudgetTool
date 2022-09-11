class Config:
    def __init__(self) -> None:
        self._settings = {
            'account_config' : 'account_config.json',
            'account_types' : ['Checking','Savings','Investments'],
            'upload_folder' : './data/upload',
            'upload_archive' : './data/upload_archive',
            'transaction_folder' : './data/transactions'
        }
        pass

    def settings(self) -> dict:
        return self._settings