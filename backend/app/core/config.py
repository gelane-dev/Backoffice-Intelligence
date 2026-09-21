from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env", "../.env"), extra="ignore")

    database_url: str = (
        "postgresql+psycopg2://backoffice:backoffice@localhost:5432/backoffice_intelligence"
    )
    secret_key: str = "troque-esta-chave-em-producao"
    access_token_expire_minutes: int = 480
    algorithm: str = "HS256"
    llm_api_key: str = ""
    llm_base_url: str = "https://api.openai.com/v1"
    llm_model: str = "gpt-4o-mini"


settings = Settings()
