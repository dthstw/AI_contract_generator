from agent_ai.prompts.contract_prompt import (
    build_lease_agreement_prompt,
    build_outsourcing_contract_prompt,
)
from langfuse import observe

@observe
def get_prompt(**kwargs) -> str:
    contract_type = kwargs.get("contract_type")
    if contract_type == "lease_agreement":
        return build_lease_agreement_prompt(**kwargs)
    elif contract_type == "outsourcing_contract":
        return build_outsourcing_contract_prompt(**kwargs)
    else:
        raise ValueError(f"Unknown contract_type: {contract_type}")
