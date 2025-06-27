from agents import Agent
from tools.save_tool import save_str_to_disc

def create_contract_agent(prompt: str, directory: str = "contracts") -> Agent:
    """
    Creates and configures an AI agent specifically for contract generation.

    The agent is initialized with a given set of instructions (prompt)
    and registered with the `save_str_to_disc` tool.

    Args:
        prompt (str): The instructions for the agent, which dictate the
                      content and style of the contract to be generated.
        directory (str): The directory where contracts will be saved.
                        Defaults to "contracts".

    Returns:
        Agent: An instance of the configured Agent.
    """
    # Update the prompt to include the directory information
    enhanced_prompt = f"{prompt}\n\nWhen saving contracts, use the directory: {directory}"
    
    return Agent(
        name="ContractAgent",
        instructions=enhanced_prompt,
        tools=[save_str_to_disc]
    )