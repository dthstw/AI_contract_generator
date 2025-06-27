import asyncio
from cli import parse_args
from core.agent_runner import run_contract
from custom_agents.contract_review_agent import ContractReviewAgent
from langfuse import get_client
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List, Optional

load_dotenv()

async def async_main(contract_request: Optional[BaseModel] = None):
    """
    Main asynchronous function to run the contract generation application.

    This function parses command-line arguments, initiates a Langfuse trace,
    runs the contract generation process, and handles potential errors,
    logging all relevant information to Langfuse.
    """
    langfuse = get_client()

    with langfuse.start_as_current_span(name="app_run") as app_span:
        if contract_request is None:
            args = parse_args()
            # Get the command BEFORE filtering args
            command = getattr(args, 'command', 'generate_contract')
            
            # Filter out the 'command' argument which is not needed by run_contract's
            # internal functions (like get_prompt and build_filename).
            filtered_args = vars(args).copy()
            if 'command' in filtered_args:
                del filtered_args['command']
        else:
            # contract_request.model_dump() already returns a dict, so use it directly
            filtered_args = contract_request.model_dump()
            command = 'generate_contract'  # Default for API calls
            
        app_span.update_trace(input=filtered_args) # Correctly pass filtered args for trace input

        try:
            if command == 'review_contract':
                # Handle contract review
                review_agent = ContractReviewAgent()
                contract_file = filtered_args.get('contract_file')
                review_type = filtered_args.get('review_type', 'comprehensive')
                
                if not contract_file:
                    raise RuntimeError("Contract file path is required for review")
                
                print(f"Reviewing contract: {contract_file}")
                result = await review_agent.review_contract(contract_file, review_type)
                print("Contract Review Results:")
                print("=" * 50)
                print(result)
                print("=" * 50)
                
                message = f"Contract review completed for: {contract_file}"
                app_span.update(output={"status": "success", "message": message, "review_result": result})
                app_span.update_trace(output={"status": "success", "message": message})
                
            else:
                # Handle contract generation (existing functionality)
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

def main(contract_request: Optional[BaseModel] = None): 
    """
    Synchronous entry point for the command-line interface.
    It runs the async_main coroutine using asyncio.
    """
    asyncio.run(async_main(contract_request))

if __name__ == "__main__":
    main()