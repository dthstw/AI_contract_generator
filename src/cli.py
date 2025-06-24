import argparse

def number_of_words_validator(value: str) -> int:
    try:
        ivalue = int(value)
        if ivalue <= 25:
            raise argparse.ArgumentTypeError("number_of_words must be greater than 25.")
        return ivalue
    except ValueError:
        raise argparse.ArgumentTypeError("number_of_words must be an integer.")

def non_empty_string(value: str) -> str:
    if not value.strip():
        raise argparse.ArgumentTypeError("This field cannot be empty or whitespace.")
    return value

def parse_args():
    """
    Parse CLI arguments and enforce validation rules for:
    - contract_type (must be one of two allowed types)
    - number_of_words (must be int > 25)
    - party_a and party_b (must be non-empty strings)

    Returns:
        argparse.Namespace: validated arguments
    """
    parser = argparse.ArgumentParser(description="📄 Generate a Japanese business contract")

    parser.add_argument(
        "--contract_type",
        required=True,
        choices=["lease_agreement", "outsourcing_contract"],
        help="Type of contract to generate: lease_agreement or outsourcing_contract"
    )

    parser.add_argument(
        "--number_of_words",
        required=True,
        type=number_of_words_validator,
        help="Approximate number of words in the contract (must be > 25)"
    )

    parser.add_argument(
        "--party_a",
        required=True,
        type=non_empty_string,
        help="Name of Party A (must not be empty)"
    )

    parser.add_argument(
        "--party_b",
        required=True,
        type=non_empty_string,
        help="Name of Party B (must not be empty)"
    )

    return parser.parse_args()