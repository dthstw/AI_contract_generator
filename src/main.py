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
from config.model_provider import CustomModelProvider


CUSTOM_MODEL_PROVIDER = CustomModelProvider()

parser = argparse.ArgumentParser(description="Generate two types of contracts")

parser.add_argument('-c', '--Args',
                nargs=4,
                type=str,
                help='Specify contract_type, desired number_of_words, party_a, party_b')

args = parser.parse_args()

arguments = vars(parser.parse_args())

# Save document tool
@function_tool
def save_str_to_disc(document: str, filename: str, directory: str = "contracts") -> str:
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, filename)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(document) 
        
    return f"Contract saved to: {path}"


# Prompt generation
def build_generation_prompt(contract_type: str, number_of_words: int, party_a: str, party_b: str) -> str:
    return (
        f"Generate an English {contract_type.replace('_', ' ')} contract with approximately {number_of_words} words.\n"
        f"Party A: {party_a}\nParty B: {party_b}\n"
        f"After generating, save it to the local disc using the available tool."
    )
    
    
# Filename generation
def build_filename(contract_type: str, party_a: str, party_b: str) -> str:
    date_str = datetime.now().strftime("%Y%m%d")
    return f"{contract_type}_{date_str}_{party_a}_{party_b}.txt"




async def main():
    
    agent = Agent(name="Assistant", instructions=build_generation_prompt(arguments["Args"][0], int(arguments["Args"][1]), arguments["Args"][2], arguments["Args"][3]), tools=[save_str_to_disc])

    # This will use the custom model provider
    result = await Runner.run(
        agent,
        "Generate loan agreement in save it in the local disc",
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
