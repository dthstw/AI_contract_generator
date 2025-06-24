import json
from agents import Runner, RunConfig
from src.prompts.dispatcher import get_prompt
from src.prompts.contract_prompt import build_filename
from src.agents.contract_agent import create_contract_agent
from src.config.model_provider import CustomModelProvider

CUSTOM_MODEL_PROVIDER = CustomModelProvider()

async def run_contract(args: dict) -> str:
    prompt = get_prompt(**args)
    filename = build_filename(**args)
    agent = create_contract_agent(prompt)

    try:
        result = await Runner.run(
            agent,
            input=(
                f"Use the `save_str_to_disc` tool to save the contract.\n"
                f"Use the filename: {filename}.\n"
                f"Only return the result from the tool call."
            ),
            run_config=RunConfig(model_provider=CUSTOM_MODEL_PROVIDER),
        )

        # Defensive parse
        output = json.loads(result.final_output)
        return output.get("message", "No message returned from tool.")

    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse LLM output: {result.final_output}") from e
    except Exception as e:
        raise RuntimeError(f"Contract generation failed: {e}")
