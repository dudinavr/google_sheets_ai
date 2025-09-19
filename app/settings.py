from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SHEET_ID: str
    OPENAI_KEY: str

    model_config = SettingsConfigDict(env_file='.env')


settings = Settings()
