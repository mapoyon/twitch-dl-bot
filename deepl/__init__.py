from config import Config


class DeepL:
    def __init__(self):
        config = Config()
        self.auth_key = config.deepl_auth_key
        self.config = config
