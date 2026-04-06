from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application configuration using Pydantic Settings.
    Values are loaded from environment variables and a .env file.
    """
    # App Settings
    app_name: str = "BasketballAI"
    debug: bool = True

    # OpenAI Settings
    # the key is mandatory
    openai_api_key: str
    model_name: str = "gpt-4o"

    # Configuration for loading the environment data, prefix to prevent from global collisions that might happen
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="BA_"
    )

@lru_cache
def get_settings():
    """
    ensures the Settings will be created once and only when the get_settings function is called and not automatically
    """
    return Settings()