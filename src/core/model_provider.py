# src/core/model_provider.py
import os
from langfuse.openai import openai
from agents import (
    Model,
    ModelProvider,
    OpenAIChatCompletionsModel,
)

class OpenAIModelProvider(ModelProvider):
    """
    Provides an OpenAI chat completions model for the agent.
    """
    def __init__(self): # Removed max_output_tokens from __init__
        self.client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model_name = os.getenv("OPENAI_MODEL", "gpt-4o")
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.2")) # Keep temperature here for default

    # Simplified get_model to reflect what OpenAIChatCompletionsModel.__init__ seems to accept
    def get_model(self, model_name: str | None = None) -> Model: # Removed max_output_tokens from get_model
        """
        Retrieves an OpenAI chat completions model instance.
        """
        # Parameters like temperature and max_tokens will now be passed via RunConfig's model_kwargs
        # if the Runner correctly forwards them to the underlying OpenAI API call.
        return OpenAIChatCompletionsModel(
            model=model_name or self.model_name,
            openai_client=self.client,
        )