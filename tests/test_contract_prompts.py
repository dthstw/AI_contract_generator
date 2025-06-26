import pytest
import re
from datetime import datetime
from src.prompts.contract_prompt import (
    build_filename,
    build_lease_agreement_prompt,
    build_outsourcing_contract_prompt,
    _sanitize_filename_part
)


class TestBuildFilename:
    """Test suite for filename generation."""
    
    def test_build_filename_format(self):
        """Test basic filename format."""
        filename = build_filename("lease_agreement", 1000, "A社", "B社")
        
        assert filename.startswith("lease_agreement_")
        assert filename.endswith("A社_B社.txt")
        assert filename.count("_") == 4  # contract, date, party_a, party_b
    
    def test_build_filename_with_date(self):
        """Test that filename includes current date."""
        filename = build_filename("outsourcing_contract", 1500, "Client", "Contractor")
        
        # Extract date part
        date_str = datetime.now().strftime("%Y%m%d")
        assert date_str in filename
    
    def test_build_filename_sanitization(self):
        """Test that party names are properly sanitized."""
        filename = build_filename("lease_agreement", 1000, "Party A & Co.", "Party B/Inc.")
        
        # Should not contain special characters
        assert "&" not in filename
        assert "/" not in filename
        assert "Party_A___Co_" in filename or "Party_A_Co_" in filename
        assert "Party_B_Inc_" in filename
    
    def test_build_filename_japanese_characters(self):
        """Test filename with Japanese characters."""
        filename = build_filename("lease_agreement", 1000, "株式会社レイヤーX", "田中太郎")
        
        assert "株式会社レイヤーX" in filename
        assert "田中太郎" in filename
        assert filename.endswith(".txt")
    
    def test_build_filename_empty_party_names(self):
        """Test filename with empty party names."""
        filename = build_filename("lease_agreement", 1000, "", "")
        
        # Should handle empty names gracefully
        assert filename.startswith("lease_agreement_")
        assert filename.endswith(".txt")
        # Should contain date
        date_str = datetime.now().strftime("%Y%m%d")
        assert date_str in filename
    
    def test_build_filename_long_party_names(self):
        """Test filename with very long party names."""
        long_name = "Very Long Company Name That Exceeds Normal Length Limits" * 3
        filename = build_filename("outsourcing_contract", 2000, long_name, "Short Co.")
        
        # Should still generate valid filename
        assert filename.startswith("outsourcing_contract_")
        assert filename.endswith(".txt")
        assert "Short_Co_" in filename


class TestSanitizeFilenamePart:
    """Test suite for filename sanitization."""
    
    def test_sanitize_basic_alphanumeric(self):
        """Test sanitization of basic alphanumeric strings."""
        assert _sanitize_filename_part("Company123") == "Company123"
        assert _sanitize_filename_part("ABC_Corp") == "ABC_Corp"
        assert _sanitize_filename_part("test-name") == "test-name"
    
    def test_sanitize_special_characters(self):
        """Test sanitization of special characters."""
        assert _sanitize_filename_part("A&B Company") == "A_B_Company"
        assert _sanitize_filename_part("Co./Inc.") == "Co__Inc_"
        assert _sanitize_filename_part("Name (Holdings)") == "Name__Holdings_"
    
    def test_sanitize_multiple_underscores(self):
        """Test that multiple consecutive underscores are collapsed."""
        assert _sanitize_filename_part("A___B___C") == "A_B_C"
        assert _sanitize_filename_part("Test____Name") == "Test_Name"
    
    def test_sanitize_leading_trailing_underscores(self):
        """Test that leading and trailing underscores are stripped."""
        assert _sanitize_filename_part("_Company_") == "Company"
        assert _sanitize_filename_part("___Name___") == "Name"
    
    def test_sanitize_empty_string(self):
        """Test sanitization of empty string."""
        assert _sanitize_filename_part("") == "unknown"
        assert _sanitize_filename_part("___") == "unknown"
    
    def test_sanitize_japanese_characters(self):
        """Test that Japanese characters are preserved."""
        assert _sanitize_filename_part("株式会社") == "株式会社"
        assert _sanitize_filename_part("田中太郎") == "田中太郎"
    
    def test_sanitize_mixed_characters(self):
        """Test sanitization with mixed character types."""
        result = _sanitize_filename_part("LayerX株式会社 & Co.")
        assert "LayerX株式会社" in result
        assert "&" not in result
        assert result.endswith("Co_")


class TestLeaseAgreementPrompt:
    """Test suite for lease agreement prompt generation."""
    
    def test_build_lease_agreement_prompt_contains_keywords(self):
        """Test that lease agreement prompt contains required keywords."""
        prompt = build_lease_agreement_prompt("lease_agreement", 1000, "LayerX", "LayerY")
        
        # Check party names
        assert "LayerX" in prompt
        assert "LayerY" in prompt
        
        # Check contract type
        assert "賃貸借契約書" in prompt
        
        # Check word count
        assert "1000" in prompt
        
        # Check key Japanese terms
        assert "賃貸人" in prompt
        assert "賃借人" in prompt
    
    def test_lease_agreement_prompt_structure(self):
        """Test the structure and completeness of lease agreement prompt."""
        prompt = build_lease_agreement_prompt("lease_agreement", 1500, "Owner Corp", "Tenant LLC")
        
        # Check essential sections
        required_sections = [
            "目的（第1条）",
            "対象物件（第2条）",
            "契約期間（第3条）",
            "賃料（第4条）",
            "使用目的（第7条）",
            "禁止事項（第8条）",
            "修繕義務（第9条）",
            "契約解除（第10条）",
            "原状回復義務（第11条）",
            "合意管轄（第12条）"
        ]
        
        for section in required_sections:
            assert section in prompt, f"Missing section: {section}"
    
    def test_lease_agreement_word_count_bounds(self):
        """Test that word count bounds are correctly calculated."""
        word_count = 2000
        prompt = build_lease_agreement_prompt("lease_agreement", word_count, "A", "B")
        
        # Calculate expected bounds (±5%)
        lower_bound = int(word_count * 0.95)  # 1900
        upper_bound = int(word_count * 1.05)  # 2100
        
        assert str(lower_bound) in prompt
        assert str(upper_bound) in prompt
        assert "±5%の範囲内" in prompt
    
    def test_lease_agreement_placeholder_format(self):
        """Test that placeholders are in correct format."""
        prompt = build_lease_agreement_prompt("lease_agreement", 1000, "Party A", "Party B")
        
        # Check for placeholder format
        placeholder_pattern = r"_{20,}"  # 20 or more underscores
        placeholders = re.findall(placeholder_pattern, prompt)
        
        # Should have multiple placeholders
        assert len(placeholders) > 10
        
        # Specific placeholders should exist
        assert "物件の所在地: ____________________" in prompt
        assert "月額賃料: ____________________円" in prompt
    
    def test_lease_agreement_save_instruction(self):
        """Test that save instruction is included."""
        prompt = build_lease_agreement_prompt("lease_agreement", 1000, "A", "B")
        
        assert "保存ツール" in prompt or "save" in prompt.lower()
        assert "ローカルディスク" in prompt or "local" in prompt.lower()


class TestOutsourcingContractPrompt:
    """Test suite for outsourcing contract prompt generation."""
    
    def test_build_outsourcing_contract_prompt_contains_keywords(self):
        """Test that outsourcing contract prompt contains required keywords."""
        prompt = build_outsourcing_contract_prompt("outsourcing_contract", 1500, "A社", "B社")
        
        # Check party names
        assert "A社" in prompt
        assert "B社" in prompt
        
        # Check contract type
        assert "業務委託契約書" in prompt
        
        # Check word count
        assert "1500" in prompt
        
        # Check key Japanese terms
        assert "委託者" in prompt
        assert "受託者" in prompt
    
    def test_outsourcing_contract_prompt_structure(self):
        """Test the structure of outsourcing contract prompt."""
        prompt = build_outsourcing_contract_prompt("outsourcing_contract", 2000, "Client", "Contractor")
        
        # Check essential sections
        required_sections = [
            "目的（第1条）",
            "委託業務の内容（第2条）",
            "委託期間（第3条）",
            "報酬（第4条）",
            "知的財産権の帰属（第6条）",
            "秘密保持義務（第7条）",
            "再委託（第8条）",
            "契約解除（第9条）",
            "損害賠償（第10条）",
            "反社会的勢力の排除（第11条）",
            "合意管轄（第12条）"
        ]
        
        for section in required_sections:
            assert section in prompt, f"Missing section: {section}"
    
    def test_outsourcing_contract_specific_placeholders(self):
        """Test outsourcing-specific placeholders."""
        prompt = build_outsourcing_contract_prompt("outsourcing_contract", 1500, "Client", "Contractor")
        
        # Check for outsourcing-specific placeholders
        assert "業務の具体的な範囲と詳細: ____________________" in prompt
        assert "成果物の特定: ____________________" in prompt
        assert "委託報酬: ____________________円" in prompt
    
    def test_outsourcing_contract_unique_clauses(self):
        """Test clauses unique to outsourcing contracts."""
        prompt = build_outsourcing_contract_prompt("outsourcing_contract", 1200, "A", "B")
        
        # Unique to outsourcing contracts
        assert "知的財産権" in prompt
        assert "秘密保持" in prompt
        assert "再委託" in prompt
        assert "反社会的勢力" in prompt
    
    def test_outsourcing_contract_word_count_validation(self):
        """Test word count handling in outsourcing contract."""
        test_cases = [
            (500, 475, 525),    # 500 words, ±5%
            (1000, 950, 1050),  # 1000 words, ±5%
            (3000, 2850, 3150)  # 3000 words, ±5%
        ]
        
        for word_count, lower, upper in test_cases:
            prompt = build_outsourcing_contract_prompt("outsourcing_contract", word_count, "A", "B")
            assert str(lower) in prompt
            assert str(upper) in prompt


class TestPromptComparison:
    """Test suite for comparing different prompt types."""
    
    def test_prompt_type_differences(self):
        """Test that different contract types generate different prompts."""
        lease_prompt = build_lease_agreement_prompt("lease_agreement", 1000, "A", "B")
        outsourcing_prompt = build_outsourcing_contract_prompt("outsourcing_contract", 1000, "A", "B")
        
        # Should be different
        assert lease_prompt != outsourcing_prompt
        
        # Lease-specific terms should not be in outsourcing
        assert "賃貸借契約書" not in outsourcing_prompt
        assert "賃料" not in outsourcing_prompt
        
        # Outsourcing-specific terms should not be in lease
        assert "業務委託契約書" not in lease_prompt
        assert "委託報酬" not in lease_prompt
        assert "知的財産権" not in lease_prompt
    
    def test_common_elements_in_both_prompts(self):
        """Test that both prompt types share common elements."""
        lease_prompt = build_lease_agreement_prompt("lease_agreement", 1000, "TestA", "TestB")
        outsourcing_prompt = build_outsourcing_contract_prompt("outsourcing_contract", 1000, "TestA", "TestB")
        
        # Common elements
        common_elements = [
            "TestA",
            "TestB",
            "1000",
            "日本のトップティアの企業法務弁護士",
            "±5%の範囲内",
            "____________________",
            "合意管轄",
            "契約解除"
        ]
        
        for element in common_elements:
            assert element in lease_prompt, f"Missing in lease: {element}"
            assert element in outsourcing_prompt, f"Missing in outsourcing: {element}"


class TestPromptEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_extreme_word_counts(self):
        """Test prompts with extreme word counts."""
        # Very small word count
        small_prompt = build_lease_agreement_prompt("lease_agreement", 500, "A", "B")
        assert "500" in small_prompt
        assert str(int(500 * 0.95)) in small_prompt  # 475
        
        # Very large word count
        large_prompt = build_outsourcing_contract_prompt("outsourcing_contract", 10000, "A", "B")
        assert "10000" in large_prompt
        assert str(int(10000 * 1.05)) in large_prompt  # 10500
    
    def test_special_characters_in_party_names(self):
        """Test prompts with special characters in party names."""
        special_chars_prompt = build_lease_agreement_prompt(
            "lease_agreement", 1000, 
            "Company A&B (Holdings) Ltd.", 
            "Service Provider Co., Inc."
        )
        
        # Should include the original names in the prompt content
        assert "Company A&B (Holdings) Ltd." in special_chars_prompt
        assert "Service Provider Co., Inc." in special_chars_prompt
    
    def test_unicode_and_emoji_in_names(self):
        """Test prompts with Unicode and emoji characters."""
        unicode_prompt = build_outsourcing_contract_prompt(
            "outsourcing_contract", 1500,
            "株式会社🚀LayerX",
            "田中太郎 & Associates"
        )
        
        # Should preserve Unicode characters
        assert "株式会社🚀LayerX" in unicode_prompt
        assert "田中太郎 & Associates" in unicode_prompt
    
    def test_very_long_party_names(self):
        """Test prompts with very long party names."""
        long_name_a = "A" * 200  # Very long name
        long_name_b = "B" * 200
        
        long_prompt = build_lease_agreement_prompt("lease_agreement", 1000, long_name_a, long_name_b)
        
        # Should still work and include the names
        assert long_name_a in long_prompt
        assert long_name_b in long_prompt
        assert "賃貸借契約書" in long_prompt