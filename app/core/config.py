from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "HoopsAI - Tactical Engine"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True
    # just for now this is the value
    OPENAI_API_KEY: str = "placeholder_key"
    MODEL_NAME: str = "gpt-4o"
    model_config = SettingsConfigDict(env_file=".env")
# it will be created just once
settings = Settings()