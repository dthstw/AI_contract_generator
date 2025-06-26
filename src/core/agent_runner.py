import json
import os
from agents import Runner, RunConfig, ModelSettings
from prompts.dispatcher import get_prompt
from prompts.contract_prompt import build_filename
from custom_agents.contract_agent import create_contract_agent
from .model_provider import OpenAIModelProvider # Correct relative import
from langfuse import observe, get_client

@observe
async def run_contract(args: dict) -> str:
    """
    Executes the contract generation process using an AI agent.

    Orchestrates prompt generation, agent creation, and running the agent
    to generate and save a contract. Handles errors and updates Langfuse spans.

    Args:
        args (dict): Dictionary with contract parameters (e.g., contract_type,
                     number_of_words, party_a, party_b).

    Returns:
        str: Message indicating the success of the contract saving operation.

    Raises:
        RuntimeError: If LLM output parsing fails or contract generation fails.
    """
    langfuse = get_client()

    prompt = get_prompt(**args)
    filename = build_filename(**args)
    agent = create_contract_agent(prompt)

    # Calculate max_tokens dynamically based on requested number_of_words
    requested_words = args.get("number_of_words") # Get user's requested words

    # Estimate tokens: ~2.0 tokens per Japanese word. Add a buffer (e.g., 10%)
    estimated_tokens = int(requested_words * 2.0 * 1.1)

    # Cap the estimated tokens at the model's actual max output limit (e.g., 8192 for GPT-4o)
    model_hard_max_output_limit = 8192
    final_max_tokens = min(estimated_tokens, model_hard_max_output_limit)

    try:
        run_config = RunConfig(
            model_provider=OpenAIModelProvider(),
            model_settings=ModelSettings(
                temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.2")),
                max_tokens=final_max_tokens,
            )
        )

        result = await Runner.run(
            agent,
            input=(
                f"Write at least {requested_words} of japanese words +- 5%"
                f"Use the `save_str_to_disc` tool to save the contract.\n"
                f"Use the filename: {filename}.\n"
                f"Only return the result from the tool call."
                
            ),
            run_config=run_config,
        )

        output = json.loads(result.final_output)
        message = output.get("message", "No message returned from tool.")
        document_content = output.get("document_content", "Document content not found.") # Assuming save_tool.py provides this

        langfuse.update_current_span(output={
            "tool_message": message,
            "filename": filename,
            "generated_contract": document_content # Changed from _preview to full
        })

        return message

    except json.JSONDecodeError as e:
        error_message = f"Failed to parse LLM output: {result.final_output}. Error: {e}"
        langfuse.update_current_span(level="ERROR", status_message=error_message)
        raise RuntimeError(error_message) from e
    except Exception as e:
        error_message = f"Contract generation failed: {e}"
        langfuse.update_current_span(level="ERROR", status_message=error_message)
        raise RuntimeError(error_message)