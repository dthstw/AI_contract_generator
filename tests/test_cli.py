import pytest
import argparse
from unittest.mock import patch, MagicMock
from src.cli import number_of_words_validator, non_empty_string, parse_args


# === Validator Tests ===

def test_number_of_words_valid():
    """Test valid number of words input."""
    assert number_of_words_validator("1000") == 1000
    assert number_of_words_validator("500") == 500  # Minimum valid value


def test_number_of_words_too_small():
    """Test number of words below minimum threshold."""
    with pytest.raises(argparse.ArgumentTypeError, match="must be greater than 500"):
        number_of_words_validator("499")
    
    with pytest.raises(argparse.ArgumentTypeError, match="must be greater than 500"):
        number_of_words_validator("10")


def test_number_of_words_not_integer():
    """Test non-integer input for number of words."""
    with pytest.raises(argparse.ArgumentTypeError, match="must be an integer"):
        number_of_words_validator("abc")
    
    with pytest.raises(argparse.ArgumentTypeError, match="must be an integer"):
        number_of_words_validator("123.45")


def test_number_of_words_edge_cases():
    """Test edge cases for number validation."""
    # Just at the boundary
    assert number_of_words_validator("500") == 500
    assert number_of_words_validator("501") == 501
    
    # Large numbers should work
    assert number_of_words_validator("10000") == 10000


# === String Validator Tests ===

def test_non_empty_string_valid():
    """Test valid non-empty string inputs."""
    assert non_empty_string("LayerX") == "LayerX"
    assert non_empty_string("Company ABC") == "Company ABC"
    assert non_empty_string("  Valid with spaces  ") == "  Valid with spaces  "


def test_non_empty_string_empty():
    """Test empty string validation."""
    with pytest.raises(argparse.ArgumentTypeError, match="cannot be empty"):
        non_empty_string("")


def test_non_empty_string_whitespace():
    """Test whitespace-only string validation."""
    with pytest.raises(argparse.ArgumentTypeError, match="cannot be empty"):
        non_empty_string("   ")
    
    with pytest.raises(argparse.ArgumentTypeError, match="cannot be empty"):
        non_empty_string("\t\n\r")


# === Argument Parsing Tests ===

class TestArgumentParsing:
    """Test suite for command-line argument parsing."""
    
    def test_parse_args_valid_lease_agreement(self):
        """Test parsing valid lease agreement arguments."""
        test_args = [
            "generate_contract",
            "--contract_type", "lease_agreement",
            "--number_of_words", "1000",
            "--party_a", "LayerX Corp",
            "--party_b", "Office Tenant"
        ]
        
        with patch('sys.argv', ['cli.py'] + test_args):
            args = parse_args()
            assert args.contract_type == "lease_agreement"
            assert args.number_of_words == 1000
            assert args.party_a == "LayerX Corp"
            assert args.party_b == "Office Tenant"
    
    def test_parse_args_valid_outsourcing_contract(self):
        """Test parsing valid outsourcing contract arguments."""
        test_args = [
            "generate_contract",
            "--contract_type", "outsourcing_contract",
            "--number_of_words", "1500",
            "--party_a", "Client Company",
            "--party_b", "Service Provider"
        ]
        
        with patch('sys.argv', ['cli.py'] + test_args):
            args = parse_args()
            assert args.contract_type == "outsourcing_contract"
            assert args.number_of_words == 1500
            assert args.party_a == "Client Company"
            assert args.party_b == "Service Provider"
    
    def test_parse_args_missing_required_arguments(self):
        """Test parsing with missing required arguments."""
        test_cases = [
            # Missing contract_type
            ["generate_contract", "--number_of_words", "1000", "--party_a", "A", "--party_b", "B"],
            # Missing number_of_words
            ["generate_contract", "--contract_type", "lease_agreement", "--party_a", "A", "--party_b", "B"],
            # Missing party_a
            ["generate_contract", "--contract_type", "lease_agreement", "--number_of_words", "1000", "--party_b", "B"],
            # Missing party_b
            ["generate_contract", "--contract_type", "lease_agreement", "--number_of_words", "1000", "--party_a", "A"],
        ]
        
        for test_args in test_cases:
            with patch('sys.argv', ['cli.py'] + test_args):
                with pytest.raises(SystemExit):
                    parse_args()
    
    def test_parse_args_invalid_contract_type(self):
        """Test parsing with invalid contract type."""
        test_args = [
            "generate_contract",
            "--contract_type", "invalid_contract",
            "--number_of_words", "1000",
            "--party_a", "Party A",
            "--party_b", "Party B"
        ]
        
        with patch('sys.argv', ['cli.py'] + test_args):
            with pytest.raises(SystemExit):
                parse_args()
    
    def test_parse_args_invalid_number_of_words(self):
        """Test parsing with invalid number of words."""
        test_args = [
            "generate_contract",
            "--contract_type", "lease_agreement",
            "--number_of_words", "100",  # Too small
            "--party_a", "Party A",
            "--party_b", "Party B"
        ]
        
        with patch('sys.argv', ['cli.py'] + test_args):
            with pytest.raises(SystemExit):
                parse_args()
    
    def test_parse_args_no_subcommand(self):
        """Test parsing with no subcommand provided."""
        with patch('sys.argv', ['cli.py']):
            with pytest.raises(SystemExit):
                parse_args()
    
    @patch('src.cli.get_client')
    def test_parse_args_with_langfuse_error_tracking(self, mock_get_client):
        """Test that Langfuse error tracking works correctly."""
        mock_langfuse = MagicMock()
        mock_span = MagicMock()
        mock_langfuse.start_as_current_span.return_value.__enter__.return_value = mock_span
        mock_get_client.return_value = mock_langfuse
        
        with patch('sys.argv', ['cli.py']):  # No subcommand to trigger error
            with pytest.raises(SystemExit):
                parse_args()
        
        # Verify Langfuse tracking was called
        mock_get_client.assert_called_once()
        mock_langfuse.start_as_current_span.assert_called_once_with(name="argparse_error")
    
    def test_parse_args_command_attribute_removed(self):
        """Test that the 'command' attribute is properly removed from parsed args."""
        test_args = [
            "generate_contract",
            "--contract_type", "lease_agreement",
            "--number_of_words", "1000",
            "--party_a", "Party A",
            "--party_b", "Party B"
        ]
        
        with patch('sys.argv', ['cli.py'] + test_args):
            args = parse_args()
            # Verify command attribute is not present
            assert not hasattr(args, 'command')
            # Verify other attributes are present
            assert hasattr(args, 'contract_type')
            assert hasattr(args, 'number_of_words')
            assert hasattr(args, 'party_a')
            assert hasattr(args, 'party_b')


# === Integration Tests ===

class TestCLIIntegration:
    """Integration tests for CLI functionality."""
    
    def test_japanese_characters_in_party_names(self):
        """Test handling of Japanese characters in party names."""
        test_args = [
            "generate_contract",
            "--contract_type", "lease_agreement",
            "--number_of_words", "1000",
            "--party_a", "株式会社レイヤーX",
            "--party_b", "田中太郎"
        ]
        
        with patch('sys.argv', ['cli.py'] + test_args):
            args = parse_args()
            assert args.party_a == "株式会社レイヤーX"
            assert args.party_b == "田中太郎"
    
    def test_special_characters_in_party_names(self):
        """Test handling of special characters in party names."""
        test_args = [
            "generate_contract",
            "--contract_type", "outsourcing_contract",
            "--number_of_words", "1500",
            "--party_a", "Company A&B (Holdings) Ltd.",
            "--party_b", "Service Provider Co., Inc."
        ]
        
        with patch('sys.argv', ['cli.py'] + test_args):
            args = parse_args()
            assert args.party_a == "Company A&B (Holdings) Ltd."
            assert args.party_b == "Service Provider Co., Inc."
