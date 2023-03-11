import pygsheets
import pandas as pd
import yaml

from google.oauth2 import service_account

class GoogleSheetClient():

    def __init__(self):
        self.scopes = ('https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive')
        self.authorize()

    def dictToSheet(self, dict, sheet):
        df_slack = pd.DataFrame(dict)
        old_sheet = self.sheets[sheet]
        df_sheet = old_sheet.get_as_df()
        df_new = pd.concat([df_slack, df_sheet]).drop_duplicates().reset_index(drop=True)
        print(df_new)
        self.sheets[sheet].set_dataframe(df_new, (1,1))

    def authorize(self):
        file = open("config.yaml", "r")
        config = yaml.safe_load(file)
        file.close()
        credentials = service_account.Credentials.from_service_account_info(config['google'], scopes=self.scopes)
        self.sheets = pygsheets.authorize(custom_credentials=credentials).open("Slacksitater")
