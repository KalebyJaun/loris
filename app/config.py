import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    def __init__(self):
        self.meta_acces_token = self._get_env_variable('META_ACCESS_TOKEN')
        self.meta_app_id = self._get_env_variable('META_APP_ID')
        self.meta_app_secret = self._get_env_variable('META_APP_SECRET')
        self.meta_api_version = self._get_env_variable('META_API_VERSION')
        self.meta_phone_number_id = self._get_env_variable('META_PHONE_NUMBER_ID')
        self.meta_verify_token = self._get_env_variable('META_VERIFY_TOKEN')
        self.openai_api_key = self._get_env_variable('OPENAI_API_KEY')
        self.open_ai_assistant_id = self._get_env_variable('OPENAI_ASSISTANT_ID')

    @staticmethod
    def _get_env_variable(name: str) -> str:
        value = os.getenv(name)
        if value is None:
            raise ValueError(f"Required Env Var '{name}' not found.")
        return value

# Instância global das configurações
settings = Settings()
