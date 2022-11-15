import pygsheets
import pandas as pd
import yaml

from google.oauth2 import service_account

class GoogleSheetClient():

    def __init__(self):
        self.scopes = ('https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive')
        self.authorize()

    def dictToSheet(self, dict, sheet):
        df = pd.DataFrame(dict)
        self.sheets[sheet].set_dataframe(df, (1,1))

    def authorize(self):
        file = open("config.yaml", "r")
        config = yaml.safe_load(file)
        file.close()
        credentials = service_account.Credentials.from_service_account_info(config['google'], scopes=self.scopes)
        self.sheets = pygsheets.authorize(custom_credentials=credentials).open("Slacksitater")
