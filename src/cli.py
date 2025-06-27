import argparse
import sys
from dotenv import load_dotenv
from langfuse import observe, get_client

load_dotenv()

def number_of_words_validator(value: str) -> int:
    """
    Validates that the number of words is an integer and greater than 500.
    """
    try:
        ivalue = int(value)
        if ivalue < 500:
            raise argparse.ArgumentTypeError("number_of_words must be greater than 500.")
        return ivalue
    except ValueError:
        raise argparse.ArgumentTypeError("number_of_words must be an integer.")

def non_empty_string(value: str) -> str:
    """
    Validates that a string argument is not empty or just whitespace.
    """
    if not value.strip():
        raise argparse.ArgumentTypeError("This field cannot be empty or whitespace.")
    return value

@observe
def parse_args():
    """
    Parses command-line arguments for the contract generation script.

    This function defines the expected arguments for the script using subparsers,
    validates them, and handles SystemExit errors from argparse, logging them
    to Langfuse. It also cleans the parsed arguments before returning them
    to ensure only relevant parameters are propagated.
    """
    parser = argparse.ArgumentParser(
        description="Generate a Japanese business contract."
    )

    # Create subparsers for different commands (e.g., generate_contract)
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- Subparser for 'generate_contract' command ---
    generate_parser = subparsers.add_parser(
        "generate_contract",
        help="Generate a new business contract."
    )

    generate_parser.add_argument(
        "--contract_type",
        required=True,
        choices=["lease_agreement", "outsourcing_contract"],
        help="Type of contract to generate: lease_agreement or outsourcing_contract"
    )

    generate_parser.add_argument(
        "--number_of_words",
        required=True,
        type=number_of_words_validator,
        help="Approximate number of words in the contract (must be >= 500)"
    )

    generate_parser.add_argument(
        "--party_a",
        required=True,
        type=non_empty_string,
        help="Name of Party A (must not be empty)"
    )

    generate_parser.add_argument(
        "--party_b",
        required=True,
        type=non_empty_string,
        help="Name of Party B (must not be empty)"
    )

    generate_parser.add_argument(
        "--folder_to_save",
        default="contracts",
        help="Folder to save the generated contract (default: contracts)"
    )

    try:
        parsed_args = parser.parse_args()
        # If no subcommand is given, print help and exit
        if parsed_args.command is None:
            parser.print_help()
            sys.exit(1)

        # Process parsed_args to remove the 'command' attribute
        # and return a clean Namespace or a dict
        cleaned_args = argparse.Namespace(**vars(parsed_args))
        del cleaned_args.command # Remove the 'command' attribute

        return cleaned_args # Return the cleaned Namespace
    except SystemExit as e:
        _langfuse_client = get_client()
        with _langfuse_client.start_as_current_span(name="argparse_error") as span:
            span.update(
                level="ERROR",
                status_message=f"Argparse failed due to invalid/missing arguments. Error: {e}",
                metadata={"argv": sys.argv}
            )
            _langfuse_client.update_current_trace(
                output={"status": "failed", "reason": "invalid_cli_arguments", "error": str(e)}
            )
        raise