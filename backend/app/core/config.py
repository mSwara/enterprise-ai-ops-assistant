from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv(Path(__file__).resolve().parents[3] / ".env")


class Settings(BaseSettings):
    database_url: str
    llm_api_key: str = ""
    llm_model: str = ""
    vector_db_path: str = "./data/vector_store"
    env: str = "development"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file="../.env",
        extra="ignore"
    )


settings = Settings()