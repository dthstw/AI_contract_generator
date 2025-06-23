from __future__ import annotations
import argparse
import asyncio
import os
from dotenv import load_dotenv

from openai import AsyncOpenAI

from agents import (
    Agent,
    Model,
    ModelProvider,
    OpenAIChatCompletionsModel,
    RunConfig,
    Runner,
    function_tool,
    set_tracing_disabled,
)

import datetime
from src.config.model_provider import CustomModelProvider
from src.prompts.contract_prompt import (
    build_lease_agreement_prompt,
    build_outsourcing_contract_prompt,
    build_filename
)
from src.agents.contract_agent import create_contract_agent

CUSTOM_MODEL_PROVIDER = CustomModelProvider()

def get_prompt(**kwargs) -> str:
    contract_type = kwargs.pop("contract_type", None)
    if contract_type == "lease_agreement":
        return build_lease_agreement_prompt(**kwargs)
    elif contract_type == "outsourcing_contract":
        return build_outsourcing_contract_prompt(**kwargs)
    else:
        raise ValueError(f"Unknown contract_type: {contract_type}")


async def main():
    #Argument parsing
    parser = argparse.ArgumentParser(description="Generate a contract")
    parser.add_argument("--contract_type", required=True, type=str)
    parser.add_argument("--number_of_words", required=True, type=int)
    parser.add_argument("--party_a", required=True, type=str)
    parser.add_argument("--party_b", required=True, type=str)
    args = parser.parse_args()
    
    contract_type = args.contract_type

    #Args for prompt
    args_dict = vars(args)
    
    prompt = get_prompt(**args_dict)
    
    filename = build_filename(
        contract_type=contract_type, 
        party_a=args.party_a,
        party_b=args.party_b,
    )
    
    agent = create_contract_agent(prompt)
    # This will use the custom model provider
    result = await Runner.run(
        agent,
        f"Generate contract and save it to the local disk as {filename}",
        run_config=RunConfig(model_provider=CUSTOM_MODEL_PROVIDER),
    )
    print(result.final_output)

    # If you uncomment this, it will use OpenAI directly, not the custom provider
    # result = await Runner.run(
    #     agent,
    #     "What's the weather in Tokyo?",
    # )
    # print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
