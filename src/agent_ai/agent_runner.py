import json
from agents import Runner, RunConfig
from agent_ai.prompts.dispatcher import get_prompt
from agent_ai.prompts.contract_prompt import build_filename
from agent_ai.custom_agents.contract_agent import create_contract_agent
from agent_ai.config.model_provider import OpenAIModelProvider
from langfuse import observe, get_client
import logfire

 
# Configure logfire instrumentation.
logfire.configure(
    service_name='my_agent_service', 
    send_to_logfire=False,
)
# This method automatically patches the OpenAI Agents SDK to send logs via OTLP to Langfuse.
logfire.instrument_openai_agents()

@observe
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
            run_config=RunConfig(model_provider=OpenAIModelProvider()),
        )

        # Defensive parse
        output = json.loads(result.final_output)
        return output.get("message", "No message returned from tool.")

    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse LLM output: {result.final_output}") from e
    except Exception as e:
        raise RuntimeError(f"Contract generation failed: {e}")
    
langfuse = get_client()
langfuse.flush()
    

