from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openai_api_key: str = ""
    openai_text_model: str = "gpt-5.6-luna"
    gemini_api_key: str = ""
    google_api_key: str = ""
    llm_provider: str = "gemini"
    gemini_text_model: str = "gemini-3.8-flash"
    case_generator_provider: str = ""
    case_validator_provider: str = ""
    action_router_provider: str = ""
    npc_provider: str = ""
    narrator_provider: str = ""
    case_generator_model: str = ""
    case_validator_model: str = ""
    action_router_model: str = ""
    npc_model: str = ""
    narrator_model: str = ""
    image_provider: str = "placeholder"
    gemini_image_model: str = "gemini-3.1-flash-lite-image"
    use_mock_llm: bool = True
    database_url: str = "data/case_unknown.db"
    data_dir: Path = Path("data/cases")
    max_graph_steps: int = 12
    max_generation_attempts: int = 3

    @property
    def effective_gemini_api_key(self) -> str:
        return self.gemini_api_key or self.google_api_key


@lru_cache
def get_settings() -> Settings:
    return Settings()
