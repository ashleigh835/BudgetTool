class Config:
    def __init__(self) -> None:
        self._settings = {
            'account_config' : 'account_config.json'
        }
        pass

    def settings(self) -> dict:
        return self._settings