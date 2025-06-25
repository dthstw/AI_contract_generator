
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import (
    Model,
    ModelProvider,
    OpenAIChatCompletionsModel,
)
from agent_ai.langfuse_provider import langfuse


load_dotenv()

class OpenAIModelProvider(ModelProvider):
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model_name = os.getenv("OPENAI_MODEL", "gpt-4o")

    def get_model(self, model_name: str | None = None) -> Model:
        return OpenAIChatCompletionsModel(
            model=model_name or self.model_name,
            openai_client=self.client,
        )