import pandas as pd

class Account(object):

    def __init__(self, csv_path) -> None:
        self._path = csv_path
        self._df = self._import_from_csv()
        pass

    def _import_from_csv(self) -> pd.DataFrame():
        return pd.read_csv(self._path)