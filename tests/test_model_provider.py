import pytest
import os
from unittest.mock import patch, MagicMock, Mock
from src.core.model_provider import OpenAIModelProvider
from agents import OpenAIChatCompletionsModel


class TestOpenAIModelProvider:
    """Test suite for OpenAI model provider."""
    
    def setup_method(self):
        """Setup method run before each test."""
        # Clear environment variables to ensure clean test state
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        if 'OPENAI_MODEL' in os.environ:
            del os.environ['OPENAI_MODEL']
        if 'OPENAI_TEMPERATURE' in os.environ:
            del os.environ['OPENAI_TEMPERATURE']
    
    @patch('src.core.model_provider.openai.AsyncOpenAI')
    def test_init_with_environment_variables(self, mock_openai):
        """Test initialization with environment variables set."""
        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'test-api-key',
            'OPENAI_MODEL': 'gpt-4-turbo',
            'OPENAI_TEMPERATURE': '0.5'
        }):
            provider = OpenAIModelProvider()
            
            # Verify initialization
            mock_openai.assert_called_once_with(api_key='test-api-key')
            assert provider.model_name == 'gpt-4-turbo'
            assert provider.temperature == 0.5
    
    @patch('src.core.model_provider.openai.AsyncOpenAI')
    def test_init_with_defaults(self, mock_openai):
        """Test initialization with default values when env vars not set."""
        provider = OpenAIModelProvider()
        
        # Verify defaults are used
        mock_openai.assert_called_once_with(api_key=None)  # os.getenv returns None
        assert provider.model_name == 'gpt-4o'  # Default value
        assert provider.temperature == 0.2  # Default value
    
    @patch('src.core.model_provider.openai.AsyncOpenAI')
    def test_init_with_invalid_temperature(self, mock_openai):
        """Test initialization with invalid temperature value."""
        with patch.dict(os.environ, {'OPENAI_TEMPERATURE': 'invalid'}):
            with pytest.raises(ValueError):
                OpenAIModelProvider()
    
    @patch('src.core.model_provider.openai.AsyncOpenAI')
    def test_get_model_default(self, mock_openai):
        """Test getting model with default model name."""
        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'test-key',
            'OPENAI_MODEL': 'gpt-4o'
        }):
            provider = OpenAIModelProvider()
            model = provider.get_model()
            
            # Verify model creation
            assert isinstance(model, OpenAIChatCompletionsModel)
    
    @patch('src.core.model_provider.openai.AsyncOpenAI')
    def test_get_model_custom_name(self, mock_openai):
        """Test getting model with custom model name."""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            provider = OpenAIModelProvider()
            model = provider.get_model('gpt-3.5-turbo')
            
            # Verify model creation with custom name
            assert isinstance(model, OpenAIChatCompletionsModel)
    
    @patch('src.core.model_provider.openai.AsyncOpenAI')
    def test_get_model_none_uses_default(self, mock_openai):
        """Test that passing None to get_model uses the default model name."""
        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'test-key',
            'OPENAI_MODEL': 'gpt-4-turbo'
        }):
            provider = OpenAIModelProvider()
            model = provider.get_model(None)
            
            assert isinstance(model, OpenAIChatCompletionsModel)
    
    @patch('src.core.model_provider.openai.AsyncOpenAI')
    def test_client_initialization(self, mock_openai):
        """Test that the OpenAI client is properly initialized."""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            provider = OpenAIModelProvider()
            
            assert provider.client == mock_client
            mock_openai.assert_called_once_with(api_key='test-key')
    
    @patch('src.core.model_provider.openai.AsyncOpenAI')
    def test_temperature_conversion(self, mock_openai):
        """Test that temperature is properly converted to float."""
        test_cases = [
            ('0.1', 0.1),
            ('0.9', 0.9),
            ('1.0', 1.0),
            ('0', 0.0),
            ('1', 1.0)
        ]
        
        for temp_str, expected_float in test_cases:
            with patch.dict(os.environ, {'OPENAI_TEMPERATURE': temp_str}):
                provider = OpenAIModelProvider()
                assert provider.temperature == expected_float
                assert isinstance(provider.temperature, float)


class TestOpenAIModelProviderIntegration:
    """Integration tests for OpenAI model provider."""
    
    @patch('src.core.model_provider.openai.AsyncOpenAI')
    def test_full_workflow(self, mock_openai):
        """Test the complete workflow of creating and using the provider."""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'sk-test123',
            'OPENAI_MODEL': 'gpt-4o',
            'OPENAI_TEMPERATURE': '0.3'
        }):
            # Initialize provider
            provider = OpenAIModelProvider()
            
            # Verify initialization
            assert provider.model_name == 'gpt-4o'
            assert provider.temperature == 0.3
            assert provider.client == mock_client
            
            # Get model
            model = provider.get_model()
            assert isinstance(model, OpenAIChatCompletionsModel)
            
            # Get model with custom name
            custom_model = provider.get_model('gpt-3.5-turbo')
            assert isinstance(custom_model, OpenAIChatCompletionsModel)
    
    @patch('src.core.model_provider.openai.AsyncOpenAI')
    def test_missing_api_key_handling(self, mock_openai):
        """Test behavior when API key is missing."""
        # This should not raise an error during initialization
        # The error would occur when making actual API calls
        provider = OpenAIModelProvider()
        
        # Should still be able to create the provider
        assert provider.model_name == 'gpt-4o'
        assert provider.temperature == 0.2
        
        # Should still be able to get a model instance
        model = provider.get_model()
        assert isinstance(model, OpenAIChatCompletionsModel)


class TestOpenAIModelProviderEdgeCases:
    """Test edge cases and error conditions."""
    
    @patch('src.core.model_provider.openai.AsyncOpenAI')
    def test_extreme_temperature_values(self, mock_openai):
        """Test handling of extreme temperature values."""
        test_cases = [
            ('0.0', 0.0),
            ('2.0', 2.0),
            ('-1.0', -1.0),  # Invalid but should not crash initialization
            ('999.9', 999.9)
        ]
        
        for temp_str, expected in test_cases:
            with patch.dict(os.environ, {'OPENAI_TEMPERATURE': temp_str}):
                provider = OpenAIModelProvider()
                assert provider.temperature == expected
    
    @patch('src.core.model_provider.openai.AsyncOpenAI')
    def test_empty_model_name(self, mock_openai):
        """Test handling of empty model name."""
        with patch.dict(os.environ, {'OPENAI_MODEL': ''}):
            provider = OpenAIModelProvider()
            # Empty string should be used as-is, not default
            assert provider.model_name == ''
    
    @patch('src.core.model_provider.openai.AsyncOpenAI')
    def test_whitespace_model_name(self, mock_openai):
        """Test handling of whitespace-only model name."""
        with patch.dict(os.environ, {'OPENAI_MODEL': '   '}):
            provider = OpenAIModelProvider()
            assert provider.model_name == '   '
    
    @patch('src.core.model_provider.openai.AsyncOpenAI')
    def test_unicode_in_model_name(self, mock_openai):
        """Test handling of unicode characters in model name."""
        with patch.dict(os.environ, {'OPENAI_MODEL': 'gpt-4o-日本語'}):
            provider = OpenAIModelProvider()
            assert provider.model_name == 'gpt-4o-日本語'
    
    @patch('src.core.model_provider.openai.AsyncOpenAI')
    def test_client_creation_failure(self, mock_openai):
        """Test handling of client creation failure."""
        mock_openai.side_effect = Exception("Failed to create client")
        
        with pytest.raises(Exception, match="Failed to create client"):
            OpenAIModelProvider()
    
    @patch('src.core.model_provider.openai.AsyncOpenAI')
    @patch('src.core.model_provider.OpenAIChatCompletionsModel')
    def test_model_creation_failure(self, mock_model_class, mock_openai):
        """Test handling of model creation failure."""
        mock_model_class.side_effect = Exception("Failed to create model")
        
        provider = OpenAIModelProvider()
        
        with pytest.raises(Exception, match="Failed to create model"):
            provider.get_model()


# === Performance Tests ===

class TestOpenAIModelProviderPerformance:
    """Performance-related tests for the model provider."""
    
    @patch('src.core.model_provider.openai.AsyncOpenAI')
    def test_multiple_model_creation(self, mock_openai):
        """Test creating multiple models from the same provider."""
        provider = OpenAIModelProvider()
        
        # Create multiple models
        models = []
        for i in range(10):
            model = provider.get_model(f'gpt-4o-{i}')
            models.append(model)
            assert isinstance(model, OpenAIChatCompletionsModel)
        
        # All models should be different instances
        assert len(set(id(model) for model in models)) == 10
    
    @patch('src.core.model_provider.openai.AsyncOpenAI')
    def test_provider_reuse(self, mock_openai):
        """Test that the same provider can be reused multiple times."""
        provider = OpenAIModelProvider()
        
        # Use the provider multiple times
        for _ in range(5):
            model = provider.get_model()
            assert isinstance(model, OpenAIChatCompletionsModel)
        
        # Client should only be created once
        assert mock_openai.call_count == 1 