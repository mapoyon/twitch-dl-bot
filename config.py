
from configparser import ConfigParser


class Config:
    def __init__(self):
        parser = ConfigParser()
        parser.read("config.ini", "UTF-8")
        self.config = parser.defaults()

    @property
    def deepl_auth_key(self):
        return self.config["deepl_auth_key"]

    @property
    def twitch_account_name(self):
        return self.config["twitch_account_name"]

    @property
    def twitch_oauth_password(self):
        return self.config["twitch_oauth_password"]

    @property
    def twitch_channel(self):
        return self.config["twitch_channel"]

    @property
    def ignore_users(self):
        ret = []
        for s in self.config["ignore_users"].split(","):
            ret.append(s.strip())
        return ret
