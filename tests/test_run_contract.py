import pytest
import json
import os
from unittest.mock import patch, MagicMock, AsyncMock
from src.core.agent_runner import run_contract
from agents import Runner, RunConfig, ModelSettings


class TestRunContractBasic:
    """Basic tests for run_contract function."""
    
    @pytest.mark.asyncio
    async def test_run_contract_mocked(self, monkeypatch):
        """Test run_contract with mocked dependencies (original test)."""
        # Fake result to simulate what LLM would return
        class FakeResult:
            final_output = '{"message": "保存が成功しました。"}'

        # Replace Runner.run with the fake async function
        async def fake_run(agent, input, run_config):
            return FakeResult()

        monkeypatch.setattr(Runner, "run", fake_run)

        # Real function — integration without hitting LLM
        args = {
            "contract_type": "lease_agreement",
            "number_of_words": 500,
            "party_a": "LayerX",
            "party_b": "LayerY",
        }

        result = await run_contract(args)
        assert result == "保存が成功しました。"
    
    @pytest.mark.asyncio
    @patch('src.core.agent_runner.get_client')
    async def test_run_contract_success_detailed(self, mock_get_client, monkeypatch):
        """Test successful contract generation with detailed verification."""
        # Mock Langfuse client
        mock_langfuse = MagicMock()
        mock_get_client.return_value = mock_langfuse
        
        # Create a more realistic fake result
        class FakeResult:
            final_output = json.dumps({
                "message": "Contract saved successfully as lease_agreement_20241201_LayerX_Tenant.txt",
                "filename": "lease_agreement_20241201_LayerX_Tenant.txt",
                "path": "/contracts/lease_agreement_20241201_LayerX_Tenant.txt"
            })

        async def fake_run(agent, input, run_config):
            # Verify the input structure
            assert "Write at least 1000 of japanese words" in input
            assert "save_str_to_disc" in input
            assert isinstance(run_config, RunConfig)
            assert hasattr(run_config, 'model_settings')
            assert hasattr(run_config.model_settings, 'max_tokens')
            return FakeResult()

        monkeypatch.setattr(Runner, "run", fake_run)

        args = {
            "contract_type": "lease_agreement",
            "number_of_words": 1000,
            "party_a": "LayerX",
            "party_b": "Tenant",
        }

        result = await run_contract(args)
        assert result == "Contract saved successfully as lease_agreement_20241201_LayerX_Tenant.txt"
        
        # Verify Langfuse span was updated
        mock_langfuse.update_current_span.assert_called_once()
        
    @pytest.mark.asyncio
    @patch('src.core.agent_runner.get_client')
    async def test_run_contract_outsourcing(self, mock_get_client, monkeypatch):
        """Test outsourcing contract generation."""
        mock_langfuse = MagicMock()
        mock_get_client.return_value = mock_langfuse
        
        class FakeResult:
            final_output = json.dumps({
                "message": "業務委託契約書を正常に保存しました",
                "document_content": "業務委託契約書の内容..."
            })

        async def fake_run(agent, input, run_config):
            return FakeResult()

        monkeypatch.setattr(Runner, "run", fake_run)

        args = {
            "contract_type": "outsourcing_contract",
            "number_of_words": 1500,
            "party_a": "クライアント会社",
            "party_b": "サービス提供会社",
        }

        result = await run_contract(args)
        assert result == "業務委託契約書を正常に保存しました"


class TestRunContractTokenCalculation:
    """Test token calculation logic."""
    
    @pytest.mark.asyncio
    @patch('src.core.agent_runner.get_client')
    async def test_token_calculation_various_word_counts(self, mock_get_client, monkeypatch):
        """Test token calculation with various word counts."""
        mock_langfuse = MagicMock()
        mock_get_client.return_value = mock_langfuse
        
        captured_configs = []
        
        class FakeResult:
            final_output = '{"message": "Success"}'

        async def fake_run(agent, input, run_config):
            captured_configs.append(run_config)
            return FakeResult()

        monkeypatch.setattr(Runner, "run", fake_run)

        test_cases = [
            (500, 1100),    # 500 * 2.0 * 1.1 = 1100
            (1000, 2200),   # 1000 * 2.0 * 1.1 = 2200
            (2000, 4400),   # 2000 * 2.0 * 1.1 = 4400
            (5000, 8192),   # 5000 * 2.0 * 1.1 = 11000, but capped at 8192
            (10000, 8192),  # Should be capped at model limit
        ]

        for word_count, expected_tokens in test_cases:
            args = {
                "contract_type": "lease_agreement",
                "number_of_words": word_count,
                "party_a": "Party A",
                "party_b": "Party B",
            }
            
            await run_contract(args)
            
            # Check the captured run_config
            config = captured_configs[-1]
            assert config.model_settings.max_tokens == expected_tokens
            
            captured_configs.clear()  # Clear for next iteration
    
    @pytest.mark.asyncio
    @patch('src.core.agent_runner.get_client')
    @patch.dict(os.environ, {'OPENAI_TEMPERATURE': '0.7'})
    async def test_temperature_from_environment(self, mock_get_client, monkeypatch):
        """Test that temperature is correctly read from environment."""
        mock_langfuse = MagicMock()
        mock_get_client.return_value = mock_langfuse
        
        captured_config = None
        
        class FakeResult:
            final_output = '{"message": "Success"}'

        async def fake_run(agent, input, run_config):
            nonlocal captured_config
            captured_config = run_config
            return FakeResult()

        monkeypatch.setattr(Runner, "run", fake_run)

        args = {
            "contract_type": "lease_agreement",
            "number_of_words": 1000,
            "party_a": "A",
            "party_b": "B",
        }
        
        await run_contract(args)
        
        # Verify temperature was set from environment
        assert captured_config is not None
        assert captured_config.model_settings is not None
        assert captured_config.model_settings.temperature == 0.7


class TestRunContractErrorHandling:
    """Test error handling scenarios."""
    
    @pytest.mark.asyncio
    @patch('src.core.agent_runner.get_client')
    async def test_json_decode_error(self, mock_get_client, monkeypatch):
        """Test handling of JSON decode errors."""
        mock_langfuse = MagicMock()
        mock_get_client.return_value = mock_langfuse
        
        class FakeResult:
            final_output = "This is not valid JSON"

        async def fake_run(agent, input, run_config):
            return FakeResult()

        monkeypatch.setattr(Runner, "run", fake_run)

        args = {
            "contract_type": "lease_agreement",
            "number_of_words": 1000,
            "party_a": "A",
            "party_b": "B",
        }

        with pytest.raises(RuntimeError, match="Failed to parse LLM output"):
            await run_contract(args)
            
        # Verify error was logged to Langfuse
        mock_langfuse.update_current_span.assert_called_once()
        call_args = mock_langfuse.update_current_span.call_args[1]
        assert call_args["level"] == "ERROR"
        assert "Failed to parse LLM output" in call_args["status_message"]
    
    @pytest.mark.asyncio
    @patch('src.core.agent_runner.get_client')
    async def test_runner_exception(self, mock_get_client, monkeypatch):
        """Test handling of exceptions from Runner.run."""
        mock_langfuse = MagicMock()
        mock_get_client.return_value = mock_langfuse
        
        async def fake_run_with_error(agent, input, run_config):
            raise Exception("API call failed")

        monkeypatch.setattr(Runner, "run", fake_run_with_error)

        args = {
            "contract_type": "outsourcing_contract",
            "number_of_words": 1500,
            "party_a": "Client",
            "party_b": "Contractor",
        }

        with pytest.raises(RuntimeError, match="Contract generation failed"):
            await run_contract(args)
            
        # Verify error was logged to Langfuse
        mock_langfuse.update_current_span.assert_called_once()
        call_args = mock_langfuse.update_current_span.call_args[1]
        assert call_args["level"] == "ERROR"
        assert "Contract generation failed" in call_args["status_message"]
    
    @pytest.mark.asyncio
    @patch('src.core.agent_runner.get_client')
    async def test_missing_message_field(self, mock_get_client, monkeypatch):
        """Test handling when LLM response doesn't have message field."""
        mock_langfuse = MagicMock()
        mock_get_client.return_value = mock_langfuse
        
        class FakeResult:
            final_output = json.dumps({
                "filename": "test.txt",
                "path": "/contracts/test.txt"
                # Missing 'message' field
            })

        async def fake_run(agent, input, run_config):
            return FakeResult()

        monkeypatch.setattr(Runner, "run", fake_run)

        args = {
            "contract_type": "lease_agreement",
            "number_of_words": 1000,
            "party_a": "A",
            "party_b": "B",
        }

        result = await run_contract(args)
        assert result == "No message returned from tool."


class TestRunContractEdgeCases:
    """Test edge cases and boundary conditions."""
    
    @pytest.mark.asyncio
    @patch('src.core.agent_runner.get_client')
    async def test_japanese_party_names(self, mock_get_client, monkeypatch):
        """Test with Japanese party names."""
        mock_langfuse = MagicMock()
        mock_get_client.return_value = mock_langfuse
        
        class FakeResult:
            final_output = json.dumps({
                "message": "日本語の契約書を保存しました",
                "document_content": "契約書の内容（日本語）"
            })

        async def fake_run(agent, input, run_config):
            return FakeResult()

        monkeypatch.setattr(Runner, "run", fake_run)

        args = {
            "contract_type": "lease_agreement",
            "number_of_words": 1000,
            "party_a": "株式会社レイヤーX",
            "party_b": "田中太郎",
        }

        result = await run_contract(args)
        assert result == "日本語の契約書を保存しました"
        
        # Verify Langfuse span includes Japanese content
        mock_langfuse.update_current_span.assert_called_once()
        call_args = mock_langfuse.update_current_span.call_args[1]
        assert "日本語の契約書を保存しました" in str(call_args["output"])
    
    @pytest.mark.asyncio
    @patch('src.core.agent_runner.get_client')
    async def test_special_characters_in_names(self, mock_get_client, monkeypatch):
        """Test with special characters in party names."""
        mock_langfuse = MagicMock()
        mock_get_client.return_value = mock_langfuse
        
        class FakeResult:
            final_output = '{"message": "Contract saved with special chars"}'

        async def fake_run(agent, input, run_config):
            return FakeResult()

        monkeypatch.setattr(Runner, "run", fake_run)

        args = {
            "contract_type": "outsourcing_contract",
            "number_of_words": 1500,
            "party_a": "Company A&B (Holdings) Ltd.",
            "party_b": "Service Provider Co., Inc.",
        }

        result = await run_contract(args)
        assert result == "Contract saved with special chars"
    
    @pytest.mark.asyncio
    @patch('src.core.agent_runner.get_client')
    async def test_minimum_word_count(self, mock_get_client, monkeypatch):
        """Test with minimum allowed word count."""
        mock_langfuse = MagicMock()
        mock_get_client.return_value = mock_langfuse
        
        class FakeResult:
            final_output = '{"message": "Minimum contract saved"}'

        async def fake_run(agent, input, run_config):
            # Verify minimum token calculation
            assert run_config.model_settings.max_tokens == 1100  # 500 * 2.0 * 1.1
            return FakeResult()

        monkeypatch.setattr(Runner, "run", fake_run)

        args = {
            "contract_type": "lease_agreement",
            "number_of_words": 500,  # Minimum allowed
            "party_a": "A",
            "party_b": "B",
        }

        result = await run_contract(args)
        assert result == "Minimum contract saved"
    
    @pytest.mark.asyncio
    @patch('src.core.agent_runner.get_client')
    async def test_maximum_word_count(self, mock_get_client, monkeypatch):
        """Test with very large word count."""
        mock_langfuse = MagicMock()
        mock_get_client.return_value = mock_langfuse
        
        class FakeResult:
            final_output = '{"message": "Large contract saved"}'

        async def fake_run(agent, input, run_config):
            # Should be capped at model limit
            assert run_config.model_settings.max_tokens == 8192
            return FakeResult()

        monkeypatch.setattr(Runner, "run", fake_run)

        args = {
            "contract_type": "outsourcing_contract",
            "number_of_words": 50000,  # Very large
            "party_a": "A",
            "party_b": "B",
        }

        result = await run_contract(args)
        assert result == "Large contract saved"


class TestRunContractIntegration:
    """Integration tests that test the full flow without heavy mocking."""
    
    @pytest.mark.asyncio
    @patch('src.core.agent_runner.get_client')
    async def test_full_workflow_integration(self, mock_get_client, monkeypatch):
        """Test complete workflow with minimal mocking."""
        mock_langfuse = MagicMock()
        mock_get_client.return_value = mock_langfuse
        
        # Only mock the final Runner.run call
        class FakeResult:
            final_output = json.dumps({
                "message": "Contract generated and saved successfully",
                "filename": "lease_agreement_20241201_TestCorp_TestTenant.txt",
                "path": "/contracts/lease_agreement_20241201_TestCorp_TestTenant.txt",
                "document_content": "賃貸借契約書\n\n第1条（目的）\n賃貸人は賃借人に対し..."
            })

        async def fake_run(agent, input, run_config):
            # Verify the complete input structure
            assert "Write at least 1200 of japanese words" in input
            assert "Use the `save_str_to_disc` tool" in input
            assert "lease_agreement_" in input
            assert "TestCorp" in input or "TestTenant" in input
            
            # Verify run_config structure
            assert isinstance(run_config, RunConfig)
            assert hasattr(run_config, 'model_provider')
            assert hasattr(run_config, 'model_settings')
            assert run_config.model_settings is not None
            assert run_config.model_settings.temperature == 0.2  # Default
            assert run_config.model_settings.max_tokens == 2640  # 1200 * 2.0 * 1.1
            
            return FakeResult()

        monkeypatch.setattr(Runner, "run", fake_run)

        # Real arguments as they would come from CLI
        args = {
            "contract_type": "lease_agreement",
            "number_of_words": 1200,
            "party_a": "TestCorp",
            "party_b": "TestTenant",
        }

        result = await run_contract(args)
        assert result == "Contract generated and saved successfully"
        
        # Verify Langfuse observability was properly used
        mock_langfuse.update_current_span.assert_called_once()
        span_args = mock_langfuse.update_current_span.call_args[1]
        assert "output" in span_args
        assert span_args["output"]["tool_message"] == "Contract generated and saved successfully"
        assert "TestCorp" in span_args["output"]["filename"] or "TestTenant" in span_args["output"]["filename"]
        assert "賃貸借契約書" in span_args["output"]["generated_contract"]
    
    @pytest.mark.asyncio
    @patch('src.core.agent_runner.get_client')
    async def test_prompt_and_filename_integration(self, mock_get_client, monkeypatch):
        """Test that prompt generation and filename building work together."""
        mock_langfuse = MagicMock()
        mock_get_client.return_value = mock_langfuse
        
        captured_input = None
        
        class FakeResult:
            final_output = '{"message": "Integration test passed"}'

        async def fake_run(agent, input, run_config):
            nonlocal captured_input
            captured_input = input
            return FakeResult()

        monkeypatch.setattr(Runner, "run", fake_run)

        args = {
            "contract_type": "outsourcing_contract",
            "number_of_words": 1800,
            "party_a": "発注者会社",
            "party_b": "受注者会社",
        }

        await run_contract(args)
        
        # Verify the input contains elements from both prompt and filename
        assert captured_input is not None
        assert "Write at least 1800 of japanese words" in captured_input
        assert "outsourcing_contract_" in captured_input
        assert "発注者会社" in captured_input or "受注者会社" in captured_input
        assert "業務委託契約書" in captured_input  # Should be in the prompt
        assert "save_str_to_disc" in captured_input