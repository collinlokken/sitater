import requests
import re
import yaml

from datetime import datetime, timedelta
from gsheetclient import GoogleSheetClient

class SlackClient():
    def __init__(self):
        self.base = "https://slack.com/api"
        self.sitater_channel_id = "C03DS3G1EUX"
        file = open("config.yaml", "r")
        config = yaml.safe_load(file)
        file.close()
        self.headers = {
            "Authorization": f"Bearer {config['slack']['token']}"
        }

        self.data = {
            "Sitat": [],
            "Author": [],
            "Reactions": [],
            "Top Reaction": [],
            "Distinct Users": [],
            "Timestamp": [],
        }

    def get_user_name_from_id(self, user_id):
        params = {
            "user": user_id
        }
        res = requests.get(f'{self.base}/users.info', params=params, headers=self.headers)
        return res.json().get("user")["real_name"]

    def replace_ats_in_text(self, text):
        if not "@" in text: return text
        p = r"\<\@(.*)\>"
        s = re.search(p, text)
        user_name = self.get_user_name_from_id(s.group(1))
        return text.replace(s.group(0), '@'+user_name)

    def extract_sitater(self):
        params = {
            "channel": self.sitater_channel_id,
            "limit":1000
        }
        res = requests.get(f'{self.base}/conversations.history', params=params, headers=self.headers)
        sitater = [sitat for sitat in res.json()["messages"] if not sitat.get("subtype")]
        for sitat in sitater:
            user_name = self.get_user_name_from_id(sitat["user"])
            text = self.replace_ats_in_text(sitat["text"])
            reactions = [reaction for reaction in sitat.get("reactions",[])]
            count = [0] # list with reactions per emoji
            user_reactions = [] # list with users reacted to post
            for reaction in reactions:
                count.append(reaction["count"])
                user_reactions += [user for user in reaction["users"]]

            dt = datetime.utcfromtimestamp(int(float(sitat["ts"]))) + timedelta(hours=1) # aaaahhhhh timezones!!!!
            timestamp = dt.strftime('%Y-%m-%d %H:%M:%S') # from unix to formated string

            self.data["Author"].append(user_name)
            self.data["Sitat"].append(text)
            self.data["Reactions"].append(sum(count))
            self.data["Top Reaction"].append(max(count))
            self.data["Distinct Users"].append(len(set(user_reactions)))
            self.data["Timestamp"].append(timestamp)

    def upload_sitater(self):
        client = GoogleSheetClient()
        client.dictToSheet(self.data, 0) # write to first (0) sheet


if __name__ == "__main__":
    slackClient = SlackClient()
    slackClient.extract_sitater()
    slackClient.upload_sitater()
