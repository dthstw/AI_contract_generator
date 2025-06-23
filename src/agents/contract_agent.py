from agents import Agent
from src.tools.save_tools import save_str_to_disc

def create_contract_agent(prompt: str) -> Agent:
    return Agent(
        name="ContractAgent",
        instructions=prompt,
        tools=[save_str_to_disc]
    )

