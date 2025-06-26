import pytest
from src.core.agent_runner import run_contract
from agents import Runner

@pytest.mark.asyncio
async def test_run_contract_mocked(monkeypatch):
    # Fake result to simulate what LLM would return
    class FakeResult:
        final_output = '{"message": "保存が成功しました。"}'

    # Replace Runner.run with the fake async function
    async def fake_run(agent, input, run_config):
        return FakeResult()

    monkeypatch.setattr(Runner, "run", fake_run)

    #real function — integration without hitting LLM
    args = {
        "contract_type": "lease_agreement",
        "number_of_words": 500,
        "party_a": "LayerX",
        "party_b": "LayerY",
    }

    result = await run_contract(args)

    assert result == "保存が成功しました。"