
import os
from dotenv import load_dotenv

from openai import AsyncOpenAI

from agents import (
    Model,
    ModelProvider,
    OpenAIChatCompletionsModel,
)


load_dotenv()

class CustomModelProvider(ModelProvider):
    """Allows to use both OpenAI api key or model from OpenRouter"""
    def __init__(self):
        use_openrouter = os.getenv("USE_OPENROUTER", "false").lower() == "true"

        if use_openrouter:
            base_url = os.getenv("OPENROUTER_BASE_URL") or ""
            api_key  = os.getenv("OPENROUTER_API_KEY") or ""
            model_name = os.getenv("OPENROUTER_MODEL") or ""
            if not base_url or not api_key or not model_name:
                raise ValueError(
                    "Please set OPENROUTER_BASE_URL, OPENROUTER_API_KEY, OPENROUTER_MODEL via env var or code."
                )
        else:
            base_url = None  # This lets OpenAI SDK default to official endpoint
            api_key = os.getenv("OPENAI_API_KEY")
            model_name = os.getenv("OPENAI_MODEL", "gpt-4o")
            if not api_key or not model_name:
                raise ValueError(
                    "Please set OPENAI_API_KEY, OPENAI_MODEL also check USE_OPENROUTER=false via env var or code."
                )
        
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.model_name = model_name
        
        
    def get_model(self, model_name: str | None = None) -> Model:
        return OpenAIChatCompletionsModel(
            model=model_name or self.model_name,
            openai_client=self.client,
        )