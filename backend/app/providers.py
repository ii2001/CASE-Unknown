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


def model_for(role: ModelRole, settings: Settings, fallback: str) -> str:
    return {
        ModelRole.CASE_GENERATOR: settings.case_generator_model,
        ModelRole.CASE_VALIDATOR: settings.case_validator_model,
        ModelRole.ACTION_ROUTER: settings.action_router_model,
        ModelRole.NPC_DIALOGUE: settings.npc_model,
        ModelRole.NARRATOR: settings.narrator_model,
    }[role] or fallback


def provider_for(role: ModelRole, settings: Settings) -> str:
    return {
        ModelRole.CASE_GENERATOR: settings.case_generator_provider,
        ModelRole.CASE_VALIDATOR: settings.case_validator_provider,
        ModelRole.ACTION_ROUTER: settings.action_router_provider,
        ModelRole.NPC_DIALOGUE: settings.npc_provider,
        ModelRole.NARRATOR: settings.narrator_provider,
    }[role] or settings.llm_provider


class GoogleProvider:
    def __init__(self, settings: Settings):
        self.settings = settings

    def structured(self, role: ModelRole, schema: type[T]):
        from langchain_google_genai import ChatGoogleGenerativeAI

        model = model_for(role, self.settings, self.settings.gemini_text_model)
        return ChatGoogleGenerativeAI(model=model, google_api_key=self.settings.effective_gemini_api_key, timeout=45, max_retries=2).with_structured_output(schema)


class OpenAIProvider:
    def __init__(self, settings: Settings):
        self.settings = settings

    def structured(self, role: ModelRole, schema: type[T]):
        from langchain_openai import ChatOpenAI

        model = model_for(role, self.settings, self.settings.openai_text_model)
        return ChatOpenAI(
            model=model,
            api_key=self.settings.openai_api_key,
            timeout=45,
            max_retries=2,
        ).with_structured_output(schema, method="json_schema")


def get_text_model(role: ModelRole, schema: type[T], settings: Settings):
    if settings.use_mock_llm:
        return None
    provider = provider_for(role, settings).lower()
    if provider in {"gemini", "google"}:
        if not settings.effective_gemini_api_key:
            raise ValueError(f"GEMINI_API_KEY is required for {role}")
        return GoogleProvider(settings).structured(role, schema)
    if provider == "openai":
        if not settings.openai_api_key:
            raise ValueError(f"OPENAI_API_KEY is required for {role}")
        return OpenAIProvider(settings).structured(role, schema)
    raise ValueError(f"Unsupported configured provider: {settings.llm_provider}")
