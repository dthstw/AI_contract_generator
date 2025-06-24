from __future__ import annotations
import argparse
import asyncio
import os
from dotenv import load_dotenv
import json

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
    contract_type = kwargs.get("contract_type")
    if contract_type == "lease_agreement":
        return build_lease_agreement_prompt(**kwargs)
    elif contract_type == "outsourcing_contract":
        return build_outsourcing_contract_prompt(**kwargs)
    else:
        raise ValueError(f"Unknown contract_type: {contract_type}")
    
def number_of_words_validator(value: str) -> int:
    """
    Validate that number_of_words is an integer > 25.
    Raises a CLI-friendly error if not.
    """
    try:
        ivalue = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError("number_of_words must be an integer.")
    
    if ivalue <= 25:
        raise argparse.ArgumentTypeError("number_of_words must be greater than 25.")
    
    return ivalue

# Validator to ensure party names are not empty strings
def non_empty_string(value: str) -> str:
    """
    Validate that a string argument is not empty or whitespace.
    """
    if not value.strip():
        raise argparse.ArgumentTypeError("This field cannot be empty or whitespace.")
    return value

def parse_args():
    """
    Parse CLI arguments and enforce validation rules for:
    - contract_type (must be one of two allowed types)
    - number_of_words (must be int > 25)
    - party_a and party_b (must be non-empty strings)
    
    Returns:
        argparse.Namespace: validated arguments
    """
    parser = argparse.ArgumentParser(description="📄 Generate a Japanese business contract")

    parser.add_argument(
        "--contract_type",
        required=True,
        choices=["lease_agreement", "outsourcing_contract"],
        help="Type of contract to generate: lease_agreement or outsourcing_contract"
    )

    parser.add_argument(
        "--number_of_words",
        required=True,
        type=number_of_words_validator,
        help="Approximate number of words in the contract (must be > 25)"
    )

    parser.add_argument(
        "--party_a",
        required=True,
        type=non_empty_string,
        help="Name of Party A (must not be empty)"
    )

    parser.add_argument(
        "--party_b",
        required=True,
        type=non_empty_string,
        help="Name of Party B (must not be empty)"
    )

    return parser.parse_args()



async def main():
    args = parse_args()
    args_dict = vars(args)

    try:
        # Prompt generation
        prompt = get_prompt(**args_dict)

        # Filename generation
        filename = build_filename(
            contract_type=args.contract_type,
            party_a=args.party_a,
            party_b=args.party_b,
        )

        # Create contract agent
        agent = create_contract_agent(prompt)

        # Run agent with custom model provider
        result = await Runner.run(
            agent,
            input=(
                f"Use the `save_str_to_disc` tool to save the contract.\n"
                f"Use the filename: {filename}.\n"
                f"Only return the result from the tool call."
            ),
            run_config=RunConfig(model_provider=CUSTOM_MODEL_PROVIDER),
        )

        # Output result message
        print(json.loads(result.final_output)["message"])

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
