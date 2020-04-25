import json
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError
from config import Config


class DeepL:
    URL_BASE = "https://api.deepl.com"

    def __init__(self):
        config = Config()
        self.auth_key = config.deepl_auth_key
        self.config = config

    def authenticate(self):
        params = {"auth_key": self.auth_key}
        res = self.get("/v2/usage", params)
        return Authenticated(res["character_count"], res["character_limit"])

    def translate(self, text, source_lang="EN", target_lang="JA"):
        params = {
            "auth_key": self.auth_key,
            "text": text,
            "source_lang": source_lang,
            "target_lang": target_lang,
        }
        res = self.get("/v2/translate", params)
        result = res["translations"][0]["text"]
        return Translated(source=text, result=result, source_lang=source_lang, target_lang=target_lang)

    def get(self, path, params=None):
        url = "{}{}".format(self.URL_BASE, path)
        if params is None:
            req = Request(url)
        else:
            req = Request("{}?{}".format(url, urlencode(params)))
        try:
            with urlopen(req) as res:
                return json.load(res)
        except HTTPError as e:
            raise DeepLError(e)


class DeepLError(Exception):
    def __init__(self, cause):
        self.cause = cause

    @property
    def code(self):
        return self.cause.code

    @property
    def reason(self):
        return "DeepL HTTP Error! {}".format(self.cause.reason)


class Authenticated:
    def __init__(self, character_count, character_limit):
        self.character_count = character_count
        self.character_limit = character_limit


class Translated:
    def __init__(self, source, result, source_lang, target_lang):
        self.source = source
        self.result = result
        self.source_lang = source_lang
        self.target_lang = target_lang
