from enum import StrEnum
from typing import Protocol, TypeVar

from pydantic import BaseModel

from .config import Settings

T = TypeVar("T", bound=BaseModel)


class ModelRole(StrEnum):
    CASE_GENERATOR = "CASE_GENERATOR"
    CASE_VALIDATOR = "CASE_VALIDATOR"
    ACTION_ROUTER = "ACTION_ROUTER"
    NPC_DIALOGUE = "NPC_DIALOGUE"
    NARRATOR = "NARRATOR"


class TextProvider(Protocol):
    def structured(self, role: ModelRole, schema: type[T]): ...


class GoogleProvider:
    def __init__(self, settings: Settings):
        self.settings = settings

    def structured(self, role: ModelRole, schema: type[T]):
        from langchain_google_genai import ChatGoogleGenerativeAI

        override = {
            ModelRole.CASE_GENERATOR: self.settings.case_generator_model,
            ModelRole.CASE_VALIDATOR: self.settings.case_validator_model,
            ModelRole.ACTION_ROUTER: self.settings.action_router_model,
            ModelRole.NPC_DIALOGUE: self.settings.npc_model,
            ModelRole.NARRATOR: self.settings.narrator_model,
        }[role]
        model = override or self.settings.gemini_text_model
        return ChatGoogleGenerativeAI(model=model, google_api_key=self.settings.google_api_key, timeout=45, max_retries=2).with_structured_output(schema)


def get_text_model(role: ModelRole, schema: type[T], settings: Settings):
    if settings.use_mock_llm:
        return None
    if settings.llm_provider != "google":
        raise ValueError(f"Unsupported configured provider: {settings.llm_provider}")
    if not settings.google_api_key:
        raise ValueError("GOOGLE_API_KEY is required when USE_MOCK_LLM=false")
    return GoogleProvider(settings).structured(role, schema)
