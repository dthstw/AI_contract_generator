from prompts.contract_prompt import (
    build_lease_agreement_prompt,
    build_outsourcing_contract_prompt,
)
from langfuse import observe

@observe(name="prompt-generation", as_type="function")
def get_prompt(**kwargs) -> str:
    """
    Dispatches to the appropriate prompt construction function based on contract type.

    Args:
        **kwargs: Arbitrary keyword arguments containing contract details,
                  including 'contract_type'.

    Returns:
        str: The generated prompt string.

    Raises:
        ValueError: If an unknown contract_type is provided.
    """
    contract_type = kwargs.get("contract_type")
    if contract_type == "lease_agreement":
        return build_lease_agreement_prompt(**kwargs)
    elif contract_type == "outsourcing_contract":
        return build_outsourcing_contract_prompt(**kwargs)
    else:
        raise ValueError(f"Unknown contract_type: {contract_type}")