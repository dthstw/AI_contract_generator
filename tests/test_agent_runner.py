import pytest
import json
import os
from unittest.mock import patch, MagicMock, AsyncMock
from src.core.agent_runner import run_contract
from agents import Runner, RunConfig, ModelSettings


class TestRunContract:
    """Test suite for the run_contract function."""
    
    def setup_method(self):
        """Setup method run before each test."""
        # Mock environment variables
        self.env_patcher = patch.dict(os.environ, {
            'OPENAI_TEMPERATURE': '0.2',
            'OPENAI_API_KEY': 'test-key',
            'OPENAI_MODEL': 'gpt-4o'
        })
        self.env_patcher.start()
    
    def teardown_method(self):
        """Cleanup after each test."""
        self.env_patcher.stop()
    
    @pytest.mark.asyncio
    @patch('src.core.agent_runner.get_client')
    @patch('src.core.agent_runner.Runner.run')
    @patch('src.core.agent_runner.create_contract_agent')
    @patch('src.core.agent_runner.build_filename')
    @patch('src.core.agent_runner.get_prompt')
    async def test_run_contract_success(self, mock_get_prompt, mock_build_filename, 
                                       mock_create_agent, mock_runner_run, mock_get_client):
        """Test successful contract generation."""
        # Setup mocks
        mock_get_prompt.return_value = "Test prompt for contract generation"
        mock_build_filename.return_value = "test_contract_20241201.txt"
        mock_agent = MagicMock()
        mock_create_agent.return_value = mock_agent
        
        # Mock successful LLM response
        mock_result = MagicMock()
        mock_result.final_output = json.dumps({
            "message": "Contract saved successfully",
            "document_content": "Contract content here"
        })
        mock_runner_run.return_value = mock_result
        
        # Mock Langfuse client
        mock_langfuse = MagicMock()
        mock_get_client.return_value = mock_langfuse
        
        # Test arguments
        args = {
            "contract_type": "lease_agreement",
            "number_of_words": 1000,
            "party_a": "LayerX Corp",
            "party_b": "Tenant Company"
        }
        
        # Execute
        result = await run_contract(args)
        
        # Verify result
        assert result == "Contract saved successfully"
        
        # Verify function calls
        mock_get_prompt.assert_called_once_with(**args)
        mock_build_filename.assert_called_once_with(**args)
        mock_create_agent.assert_called_once_with("Test prompt for contract generation")
        
        # Verify Runner.run was called with correct parameters
        mock_runner_run.assert_called_once()
        call_args = mock_runner_run.call_args
        
        # Check agent argument
        assert call_args[1]['agent'] == mock_agent
        
        # Check input contains expected elements
        input_text = call_args[1]['input']
        assert "Write at least 1000 of japanese words" in input_text
        assert "test_contract_20241201.txt" in input_text
        assert "save_str_to_disc" in input_text
        
        # Check run_config
        run_config = call_args[1]['run_config']
        assert isinstance(run_config, RunConfig)
        
        # Verify Langfuse span update
        mock_langfuse.update_current_span.assert_called_once()
        span_call_args = mock_langfuse.update_current_span.call_args[1]
        assert "output" in span_call_args
        assert span_call_args["output"]["tool_message"] == "Contract saved successfully"
        assert span_call_args["output"]["filename"] == "test_contract_20241201.txt"
    
    @pytest.mark.asyncio
    @patch('src.core.agent_runner.get_client')
    @patch('src.core.agent_runner.Runner.run')
    @patch('src.core.agent_runner.create_contract_agent')
    @patch('src.core.agent_runner.build_filename')
    @patch('src.core.agent_runner.get_prompt')
    async def test_run_contract_json_decode_error(self, mock_get_prompt, mock_build_filename,
                                                 mock_create_agent, mock_runner_run, mock_get_client):
        """Test handling of JSON decode error from LLM response."""
        # Setup mocks
        mock_get_prompt.return_value = "Test prompt"
        mock_build_filename.return_value = "test_contract.txt"
        mock_create_agent.return_value = MagicMock()
        
        # Mock invalid JSON response
        mock_result = MagicMock()
        mock_result.final_output = "Invalid JSON response from LLM"
        mock_runner_run.return_value = mock_result
        
        # Mock Langfuse client
        mock_langfuse = MagicMock()
        mock_get_client.return_value = mock_langfuse
        
        args = {
            "contract_type": "lease_agreement",
            "number_of_words": 1000,
            "party_a": "Party A",
            "party_b": "Party B"
        }
        
        # Execute and expect RuntimeError
        with pytest.raises(RuntimeError, match="Failed to parse LLM output"):
            await run_contract(args)
        
        # Verify Langfuse error tracking
        mock_langfuse.update_current_span.assert_called_once()
        call_args = mock_langfuse.update_current_span.call_args[1]
        assert call_args["level"] == "ERROR"
        assert "Failed to parse LLM output" in call_args["status_message"]
    
    @pytest.mark.asyncio
    @patch('src.core.agent_runner.get_client')
    @patch('src.core.agent_runner.Runner.run')
    @patch('src.core.agent_runner.create_contract_agent')
    @patch('src.core.agent_runner.build_filename')
    @patch('src.core.agent_runner.get_prompt')
    async def test_run_contract_runner_exception(self, mock_get_prompt, mock_build_filename,
                                                mock_create_agent, mock_runner_run, mock_get_client):
        """Test handling of exceptions from Runner.run."""
        # Setup mocks
        mock_get_prompt.return_value = "Test prompt"
        mock_build_filename.return_value = "test_contract.txt"
        mock_create_agent.return_value = MagicMock()
        
        # Mock exception from Runner.run
        mock_runner_run.side_effect = Exception("API call failed")
        
        # Mock Langfuse client
        mock_langfuse = MagicMock()
        mock_get_client.return_value = mock_langfuse
        
        args = {
            "contract_type": "outsourcing_contract",
            "number_of_words": 1500,
            "party_a": "Client",
            "party_b": "Contractor"
        }
        
        # Execute and expect RuntimeError
        with pytest.raises(RuntimeError, match="Contract generation failed"):
            await run_contract(args)
        
        # Verify Langfuse error tracking
        mock_langfuse.update_current_span.assert_called_once()
        call_args = mock_langfuse.update_current_span.call_args[1]
        assert call_args["level"] == "ERROR"
        assert "Contract generation failed" in call_args["status_message"]
    
    @pytest.mark.asyncio
    @patch('src.core.agent_runner.get_client')
    @patch('src.core.agent_runner.Runner.run')
    @patch('src.core.agent_runner.create_contract_agent')
    @patch('src.core.agent_runner.build_filename')
    @patch('src.core.agent_runner.get_prompt')
    async def test_token_calculation(self, mock_get_prompt, mock_build_filename,
                                    mock_create_agent, mock_runner_run, mock_get_client):
        """Test dynamic token calculation based on word count."""
        # Setup mocks
        mock_get_prompt.return_value = "Test prompt"
        mock_build_filename.return_value = "test_contract.txt"
        mock_create_agent.return_value = MagicMock()
        
        mock_result = MagicMock()
        mock_result.final_output = json.dumps({"message": "Success"})
        mock_runner_run.return_value = mock_result
        
        mock_langfuse = MagicMock()
        mock_get_client.return_value = mock_langfuse
        
        # Test different word counts
        test_cases = [
            (500, 1100),   # 500 * 2.0 * 1.1 = 1100
            (1000, 2200),  # 1000 * 2.0 * 1.1 = 2200
            (5000, 8192),  # 5000 * 2.0 * 1.1 = 11000, but capped at 8192
        ]
        
        for word_count, expected_max_tokens in test_cases:
            args = {
                "contract_type": "lease_agreement",
                "number_of_words": word_count,
                "party_a": "Party A",
                "party_b": "Party B"
            }
            
            await run_contract(args)
            
            # Verify RunConfig with correct max_tokens
            call_args = mock_runner_run.call_args[1]
            run_config = call_args['run_config']
            assert run_config.model_settings.max_tokens == expected_max_tokens
    
    @pytest.mark.asyncio
    @patch('src.core.agent_runner.get_client')
    @patch('src.core.agent_runner.Runner.run')
    @patch('src.core.agent_runner.create_contract_agent')
    @patch('src.core.agent_runner.build_filename')
    @patch('src.core.agent_runner.get_prompt')
    async def test_temperature_from_environment(self, mock_get_prompt, mock_build_filename,
                                               mock_create_agent, mock_runner_run, mock_get_client):
        """Test that temperature is correctly read from environment."""
        # Setup mocks
        mock_get_prompt.return_value = "Test prompt"
        mock_build_filename.return_value = "test_contract.txt"
        mock_create_agent.return_value = MagicMock()
        
        mock_result = MagicMock()
        mock_result.final_output = json.dumps({"message": "Success"})
        mock_runner_run.return_value = mock_result
        
        mock_langfuse = MagicMock()
        mock_get_client.return_value = mock_langfuse
        
        # Test with different temperature values
        test_temperatures = ['0.1', '0.5', '0.9']
        
        for temp_str in test_temperatures:
            with patch.dict(os.environ, {'OPENAI_TEMPERATURE': temp_str}):
                args = {
                    "contract_type": "lease_agreement",
                    "number_of_words": 1000,
                    "party_a": "Party A",
                    "party_b": "Party B"
                }
                
                await run_contract(args)
                
                # Verify temperature in RunConfig
                call_args = mock_runner_run.call_args[1]
                run_config = call_args['run_config']
                assert run_config.model_settings.temperature == float(temp_str)


class TestRunContractIntegration:
    """Integration tests for run_contract function."""
    
    @pytest.mark.asyncio
    @patch('src.core.agent_runner.get_client')
    @patch('src.core.agent_runner.Runner.run')
    async def test_full_integration_workflow(self, mock_runner_run, mock_get_client):
        """Test the complete integration workflow without mocking internal components."""
        # Mock only the external dependencies
        mock_result = MagicMock()
        mock_result.final_output = json.dumps({
            "message": "Contract saved as lease_agreement_20241201_LayerX_Tenant.txt",
            "document_content": "契約書\n\n第1条（目的）\n..."
        })
        mock_runner_run.return_value = mock_result
        
        mock_langfuse = MagicMock()
        mock_get_client.return_value = mock_langfuse
        
        # Real arguments that would come from CLI
        args = {
            "contract_type": "lease_agreement",
            "number_of_words": 1000,
            "party_a": "LayerX",
            "party_b": "Tenant"
        }
        
        # Execute the full workflow
        result = await run_contract(args)
        
        # Verify result
        assert result == "Contract saved as lease_agreement_20241201_LayerX_Tenant.txt"
        
        # Verify Runner.run was called
        assert mock_runner_run.called
        
        # Verify the input contains Japanese instruction
        call_args = mock_runner_run.call_args[1]
        input_text = call_args['input']
        assert "Write at least 1000 of japanese words" in input_text
    
    @pytest.mark.asyncio
    @patch('src.core.agent_runner.get_client')
    async def test_missing_message_in_response(self, mock_get_client):
        """Test handling when LLM response doesn't contain expected message field."""
        with patch('src.core.agent_runner.Runner.run') as mock_runner_run:
            # Mock response without 'message' field
            mock_result = MagicMock()
            mock_result.final_output = json.dumps({
                "document_content": "Contract content",
                # Missing 'message' field
            })
            mock_runner_run.return_value = mock_result
            
            mock_langfuse = MagicMock()
            mock_get_client.return_value = mock_langfuse
            
            args = {
                "contract_type": "lease_agreement",
                "number_of_words": 1000,
                "party_a": "Party A",
                "party_b": "Party B"
            }
            
            result = await run_contract(args)
            
            # Should return default message
            assert result == "No message returned from tool."
    
    @pytest.mark.asyncio
    @patch('src.core.agent_runner.get_client')
    async def test_japanese_party_names(self, mock_get_client):
        """Test contract generation with Japanese party names."""
        with patch('src.core.agent_runner.Runner.run') as mock_runner_run:
            mock_result = MagicMock()
            mock_result.final_output = json.dumps({
                "message": "契約書が正常に保存されました",
                "document_content": "日本語の契約書内容"
            })
            mock_runner_run.return_value = mock_result
            
            mock_langfuse = MagicMock()
            mock_get_client.return_value = mock_langfuse
            
            args = {
                "contract_type": "outsourcing_contract",
                "number_of_words": 1500,
                "party_a": "株式会社レイヤーX",
                "party_b": "田中太郎"
            }
            
            result = await run_contract(args)
            
            # Should handle Japanese characters correctly
            assert result == "契約書が正常に保存されました"
            
            # Verify Langfuse span update includes Japanese content
            mock_langfuse.update_current_span.assert_called_once()
            call_args = mock_langfuse.update_current_span.call_args[1]
            assert call_args["output"]["generated_contract"] == "日本語の契約書内容"


class TestRunContractEdgeCases:
    """Test edge cases and error scenarios."""
    
    @pytest.mark.asyncio
    @patch('src.core.agent_runner.get_client')
    async def test_empty_args(self, mock_get_client):
        """Test behavior with empty arguments."""
        mock_langfuse = MagicMock()
        mock_get_client.return_value = mock_langfuse
        
        # This should raise an error from get_prompt due to missing required args
        with pytest.raises(Exception):  # Could be KeyError or TypeError
            await run_contract({})
    
    @pytest.mark.asyncio
    @patch('src.core.agent_runner.get_client')
    async def test_invalid_number_of_words(self, mock_get_client):
        """Test behavior with invalid number_of_words."""
        mock_langfuse = MagicMock()
        mock_get_client.return_value = mock_langfuse
        
        args = {
            "contract_type": "lease_agreement",
            "number_of_words": "invalid",  # Should be int
            "party_a": "Party A",
            "party_b": "Party B"
        }
        
        # This should raise an error during token calculation
        with pytest.raises(Exception):
            await run_contract(args)
    
    @pytest.mark.asyncio
    @patch('src.core.agent_runner.get_client')
    async def test_extreme_word_counts(self, mock_get_client):
        """Test behavior with extreme word count values."""
        with patch('src.core.agent_runner.Runner.run') as mock_runner_run:
            mock_result = MagicMock()
            mock_result.final_output = json.dumps({"message": "Success"})
            mock_runner_run.return_value = mock_result
            
            mock_langfuse = MagicMock()
            mock_get_client.return_value = mock_langfuse
            
            # Test very large word count
            args = {
                "contract_type": "lease_agreement",
                "number_of_words": 100000,  # Very large
                "party_a": "Party A",
                "party_b": "Party B"
            }
            
            await run_contract(args)
            
            # Should be capped at model limit
            call_args = mock_runner_run.call_args[1]
            run_config = call_args['run_config']
            assert run_config.model_settings.max_tokens == 8192  # Model hard limit 