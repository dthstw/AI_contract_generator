from agent_ai.prompts.contract_prompt import (
    build_filename,
    build_lease_agreement_prompt,
    build_outsourcing_contract_prompt
)

def test_build_filename_format():
    filename = build_filename("lease_agreement", 1000, "A社", "B社")
    
    assert filename.startswith("lease_agreement_")
    assert filename.endswith("A社_B社.txt")
    assert filename.count("_") == 4  # contract, date, party_a, party_b
    
def test_build_lease_agreement_prompt_contains_keywords():
    prompt = build_lease_agreement_prompt("lease_agreement", 1000, "LayerX", "LayerY")
    assert "LayerX" in prompt
    assert "LayerY" in prompt
    assert "賃貸借契約書" in prompt
    assert "1000" in prompt or "１０００" in prompt

def test_build_outsourcing_contract_prompt_contains_keywords():
    prompt = build_outsourcing_contract_prompt("outsourcing_contract", 1500, "A社", "B社")
    assert "A社" in prompt
    assert "B社" in prompt
    assert "業務委託契約書" in prompt
    assert "1500" in prompt or "１５００" in prompt