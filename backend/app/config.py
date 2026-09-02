from functools import lru_cache
from pathlib import Path

import yaml
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "enterprise-ai-research-agent"
    app_env: str = "development"
    database_url: str = "postgresql+psycopg2://localhost/research_agent"
    redis_url: str = "redis://localhost:6379/0"
    frontend_origin: str = "http://localhost:5173"
    groq_api_key: str | None = None
    # Use the broadly available production model unless a stronger model is
    # explicitly configured through GROQ_MODEL in the local environment.
    groq_model: str = "llama-3.1-8b-instant"
    groq_fast_model: str = "llama-3.1-8b-instant"
    max_query_chars: int = 2_000
    max_context_tokens: int = 4_000
    config_dir: Path = Path("configs/industries")
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    def industry(self, name: str) -> dict:
        path = self.config_dir / f"{name}.yaml"
        if not path.exists():
            path = self.config_dir / "default.yaml"
        return yaml.safe_load(path.read_text(encoding="utf-8"))


@lru_cache
def get_settings() -> Settings:
    return Settings()
