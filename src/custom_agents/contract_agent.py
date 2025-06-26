from agents import Agent
from tools.save_tool import save_str_to_disc

def create_contract_agent(prompt: str) -> Agent:
    """
    Creates and configures an AI agent specifically for contract generation.

    The agent is initialized with a given set of instructions (prompt)
    and registered with the `save_str_to_disc` tool.

    Args:
        prompt (str): The instructions for the agent, which dictate the
                      content and style of the contract to be generated.

    Returns:
        Agent: An instance of the configured Agent.
    """
    return Agent(
        name="ContractAgent",
        instructions=prompt,
        tools=[save_str_to_disc]
    )