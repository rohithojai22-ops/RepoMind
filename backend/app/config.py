from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    gemini_api_key: str
    gemini_model: str = "gemini-2.5-flash"
    database_url: str
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    github_token: str = ""
    top_k: int = 8
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
