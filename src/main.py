import asyncio
from cli import parse_args
from core.agent_runner import run_contract
from langfuse import get_client
from dotenv import load_dotenv

load_dotenv()

async def async_main():
    """
    Main asynchronous function to run the contract generation application.

    This function parses command-line arguments, initiates a Langfuse trace,
    runs the contract generation process, and handles potential errors,
    logging all relevant information to Langfuse.
    """
    langfuse = get_client()

    with langfuse.start_as_current_span(name="app_run") as app_span:
        args = parse_args()
        # Filter out the 'command' argument which is not needed by run_contract's
        # internal functions (like get_prompt and build_filename).
        filtered_args = vars(args).copy()
        if 'command' in filtered_args:
            del filtered_args['command']
        app_span.update_trace(input=filtered_args) # Correctly pass filtered args for trace input


        try:
            message = await run_contract(filtered_args) # Pass filtered_args
            print(f"Contract generation successful: {message}")
            app_span.update(output={"status": "success", "message": message})
            app_span.update_trace(output={"status": "success", "message": message})
        except RuntimeError as e:
            print(f"Error: {e}")
            app_span.update(level="ERROR", status_message=str(e)) # Correct for span update
            # Removed 'level="ERROR"' from update_trace as it's not supported
            app_span.update_trace(output={"status": "failed", "error": str(e)})

    langfuse.flush()

def main(): # This is the synchronous entry point for pyproject.toml
    """
    Synchronous entry point for the command-line interface.
    It runs the async_main coroutine using asyncio.
    """
    asyncio.run(async_main())

if __name__ == "__main__":
    # This block is executed when the script is run directly (e.g., `python src/main.py`).
    main()