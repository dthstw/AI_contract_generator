import pytest
from agent_ai.prompts.dispatcher import get_prompt

def test_get_prompt_lease_agreement():
    prompt = get_prompt(
        contract_type="lease_agreement",
        number_of_words=500,
        party_a="LayerX",
        party_b="LayerY",
    )
    assert "賃貸借契約書" in prompt
    assert "LayerX" in prompt and "LayerY" in prompt

def test_get_prompt_outsourcing_contract():
    prompt = get_prompt(
        contract_type="outsourcing_contract",
        number_of_words=700,
        party_a="A社",
        party_b="B社",
    )
    assert "業務委託契約書" in prompt
    assert "A社" in prompt and "B社" in prompt

def test_get_prompt_invalid_type_raises():
    with pytest.raises(ValueError, match="Unknown contract_type:"):
        get_prompt(
            contract_type="invalid_type",
            number_of_words=100,
            party_a="Foo",
            party_b="Bar",
        )