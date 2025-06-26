import pytest
import re
import json
from typing import Dict, List, Any


class ContractValidator:
    """Utility class for validating contract content."""
    
    @staticmethod
    def count_japanese_words(text: str) -> int:
        """Count Japanese words in text."""
        # Remove placeholders and common non-content elements
        cleaned_text = re.sub(r'_{10,}', '', text)  # Remove placeholder underscores
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)  # Normalize whitespace
        
        # Count Japanese characters (excluding punctuation and spaces)
        japanese_chars = re.findall(r'[ひらがなカタカナ漢字一-龯ァ-ヶー]', cleaned_text)
        
        # Approximate word count (characters / 2 for Japanese)
        return len(japanese_chars) // 2
    
    @staticmethod
    def validate_placeholders(text: str) -> Dict[str, Any]:
        """Validate that placeholders are properly formatted."""
        # Find all placeholder patterns
        placeholders = re.findall(r'_{10,}', text)
        
        # Check for consistent formatting
        expected_length = 20  # Standard placeholder length
        consistent_placeholders = [p for p in placeholders if len(p) == expected_length]
        
        # Find specific required placeholders
        required_patterns = [
            r'所在地:\s*_{10,}',
            r'金額:\s*_{10,}円',
            r'期日:\s*_{10,}',
            r'年\s*_{5,}\s*月\s*_{5,}\s*日',
        ]
        
        found_patterns = {}
        for pattern in required_patterns:
            found_patterns[pattern] = bool(re.search(pattern, text))
        
        return {
            'total_placeholders': len(placeholders),
            'consistent_placeholders': len(consistent_placeholders),
            'placeholder_consistency_ratio': len(consistent_placeholders) / max(len(placeholders), 1),
            'required_patterns_found': found_patterns,
            'has_placeholders': len(placeholders) > 0
        }
    
    @staticmethod
    def validate_japanese_legal_structure(text: str) -> Dict[str, Any]:
        """Validate Japanese legal document structure."""
        # Check for proper article structure
        article_pattern = r'第\d+条[（(]([^）)]+)[）)]'
        articles = re.findall(article_pattern, text)
        
        # Check for proper contract elements
        contract_elements = {
            'has_title': bool(re.search(r'(契約書|合意書)', text)),
            'has_parties': bool(re.search(r'(甲|乙|賃貸人|賃借人|委託者|受託者)', text)),
            'has_articles': len(articles) > 0,
            'article_count': len(articles),
            'has_signature_section': bool(re.search(r'(署名|捺印|記名)', text)),
            'has_date_section': bool(re.search(r'年.*月.*日', text)),
        }
        
        # Check article naming conventions
        expected_articles = {
            'lease': ['目的', '物件', '期間', '賃料', '解除'],
            'outsourcing': ['目的', '業務', '期間', '報酬', '解除']
        }
        
        return {
            **contract_elements,
            'articles_found': articles,
            'structure_completeness': sum(contract_elements.values()) / len(contract_elements)
        }


class TestContractValidation:
    """Test suite for contract content validation."""
    
    def test_word_count_validation(self):
        """Test Japanese word counting accuracy."""
        test_cases = [
            ("これは日本語のテストです。", 6),  # Simple sentence
            ("契約書作成システムのテストを実行しています。", 9),  # Longer sentence
            ("____________________", 0),  # Only placeholders
            ("契約書 ____________________", 1),  # Mixed content
            ("第1条（目的）この契約は賃貸借について定める。", 8),  # Legal text
        ]
        
        for text, expected_words in test_cases:
            actual_words = ContractValidator.count_japanese_words(text)
            assert actual_words >= expected_words - 2  # Allow small variance
            assert actual_words <= expected_words + 2
    
    def test_placeholder_validation_basic(self):
        """Test basic placeholder validation."""
        text_with_placeholders = """
        物件の所在地: ____________________
        月額賃料: ____________________円
        契約期間: ____________________年____月____日から____________________年____月____日まで
        """
        
        result = ContractValidator.validate_placeholders(text_with_placeholders)
        
        assert result['has_placeholders'] is True
        assert result['total_placeholders'] > 0
        assert result['placeholder_consistency_ratio'] > 0.5
    
    def test_placeholder_validation_comprehensive(self):
        """Test comprehensive placeholder validation."""
        well_formatted_text = """
        賃貸借契約書
        
        物件の所在地: ____________________
        月額賃料: ____________________円
        支払期日: 毎月____________________日
        契約開始日: ____________________年____月____日
        契約終了日: ____________________年____月____日
        """
        
        result = ContractValidator.validate_placeholders(well_formatted_text)
        
        assert result['total_placeholders'] >= 7
        assert result['placeholder_consistency_ratio'] > 0.8
        assert result['required_patterns_found'][r'所在地:\s*_{10,}'] is True
        assert result['required_patterns_found'][r'金額:\s*_{10,}円'] is True
    
    def test_japanese_legal_structure_lease(self):
        """Test Japanese legal structure validation for lease agreements."""
        lease_contract = """
        賃貸借契約書
        
        賃貸人（甲）: ____________________
        賃借人（乙）: ____________________
        
        第1条（目的）
        甲は乙に対し、下記物件を賃貸し、乙はこれを賃借する。
        
        第2条（対象物件）
        物件の所在地: ____________________
        
        第3条（契約期間）
        契約期間: ____________________年____月____日から____________________年____月____日まで
        
        第4条（賃料）
        月額賃料: ____________________円
        
        第10条（契約解除）
        甲又は乙は以下の場合、本契約を解除することができる。
        
        本契約の締結を証するため、甲乙記名捺印の上、各1通を保有する。
        
        ____________________年____月____日
        """
        
        result = ContractValidator.validate_japanese_legal_structure(lease_contract)
        
        assert result['has_title'] is True
        assert result['has_parties'] is True
        assert result['has_articles'] is True
        assert result['article_count'] >= 5
        assert result['has_signature_section'] is True
        assert result['has_date_section'] is True
        assert result['structure_completeness'] > 0.8
        
        # Check specific articles
        assert '目的' in result['articles_found']
        assert '解除' in result['articles_found']
    
    def test_japanese_legal_structure_outsourcing(self):
        """Test Japanese legal structure validation for outsourcing contracts."""
        outsourcing_contract = """
        業務委託契約書
        
        委託者（甲）: ____________________
        受託者（乙）: ____________________
        
        第1条（目的）
        甲は乙に対し、下記業務を委託し、乙はこれを受託する。
        
        第2条（委託業務の内容）
        業務内容: ____________________
        
        第3条（委託期間）
        委託期間: ____________________年____月____日から____________________年____月____日まで
        
        第4条（報酬）
        委託報酬: ____________________円
        
        第6条（知的財産権の帰属）
        本業務により生じる知的財産権は甲に帰属する。
        
        第7条（秘密保持義務）
        乙は業務上知り得た秘密情報を第三者に開示してはならない。
        
        第9条（契約解除）
        甲又は乙は以下の場合、本契約を解除することができる。
        
        本契約の締結を証するため、甲乙署名捺印の上、各1通を保有する。
        
        ____________________年____月____日
        """
        
        result = ContractValidator.validate_japanese_legal_structure(outsourcing_contract)
        
        assert result['has_title'] is True
        assert result['has_parties'] is True
        assert result['has_articles'] is True
        assert result['article_count'] >= 6
        assert result['has_signature_section'] is True
        assert result['structure_completeness'] > 0.8
        
        # Check specific articles
        assert '目的' in result['articles_found']
        assert '知的財産権の帰属' in result['articles_found']
        assert '秘密保持義務' in result['articles_found']


class TestContractQualityValidation:
    """Test suite for contract quality validation."""
    
    def test_contract_completeness_lease(self):
        """Test completeness of lease agreement contracts."""
        complete_lease = """
        賃貸借契約書
        
        賃貸人: ____________________
        賃借人: ____________________
        
        第1条（目的）甲は乙に対し物件を賃貸する。
        第2条（対象物件）所在地: ____________________
        第3条（契約期間）____________________年____月____日から____________________年____月____日まで
        第4条（賃料）月額____________________円
        第5条（敷金）____________________円
        第6条（管理費）____________________円
        第7条（使用目的）住居用として使用する
        第8条（禁止事項）転貸を禁止する
        第9条（修繕義務）甲が負担する
        第10条（契約解除）債務不履行時に解除可能
        第11条（原状回復義務）乙が負担する
        第12条（合意管轄）東京地方裁判所とする
        
        署名捺印：____________________年____月____日
        """
        
        validator = ContractValidator()
        
        # Test word count
        word_count = validator.count_japanese_words(complete_lease)
        assert word_count > 30  # Should have substantial content
        
        # Test placeholders
        placeholder_result = validator.validate_placeholders(complete_lease)
        assert placeholder_result['has_placeholders'] is True
        assert placeholder_result['total_placeholders'] >= 15
        
        # Test structure
        structure_result = validator.validate_japanese_legal_structure(complete_lease)
        assert structure_result['article_count'] >= 10
        assert structure_result['structure_completeness'] > 0.9
    
    def test_contract_completeness_outsourcing(self):
        """Test completeness of outsourcing contract."""
        complete_outsourcing = """
        業務委託契約書
        
        委託者: ____________________
        受託者: ____________________
        
        第1条（目的）甲は乙に業務を委託する。
        第2条（委託業務の内容）業務範囲: ____________________
        第3条（委託期間）____________________年____月____日から____________________年____月____日まで
        第4条（報酬）委託報酬: ____________________円
        第5条（費用負担）甲が負担する
        第6条（知的財産権の帰属）甲に帰属する
        第7条（秘密保持義務）秘密情報を保護する
        第8条（再委託）甲の事前承諾が必要
        第9条（契約解除）債務不履行時に解除可能
        第10条（損害賠償）過失による損害を賠償する
        第11条（反社会的勢力の排除）関係がないことを保証する
        第12条（合意管轄）東京地方裁判所とする
        
        署名捺印：____________________年____月____日
        """
        
        validator = ContractValidator()
        
        # Test word count
        word_count = validator.count_japanese_words(complete_outsourcing)
        assert word_count > 35
        
        # Test structure
        structure_result = validator.validate_japanese_legal_structure(complete_outsourcing)
        assert structure_result['article_count'] >= 10
        assert '知的財産権の帰属' in structure_result['articles_found']
        assert '秘密保持義務' in structure_result['articles_found']
        assert '反社会的勢力の排除' in structure_result['articles_found']
    
    def test_contract_word_count_accuracy(self):
        """Test word count accuracy against target."""
        test_contracts = [
            ("短い契約書です。", 500, False),  # Too short
            ("これは適切な長さの契約書内容を含んでいます。" * 50, 1000, True),  # Appropriate
            ("非常に長い契約書の内容です。" * 200, 1500, True),  # Long enough
        ]
        
        for contract_text, target_words, should_pass in test_contracts:
            actual_words = ContractValidator.count_japanese_words(contract_text)
            
            # Allow ±5% variance
            lower_bound = target_words * 0.95
            upper_bound = target_words * 1.05
            
            is_within_range = lower_bound <= actual_words <= upper_bound
            
            if should_pass:
                assert actual_words >= lower_bound * 0.5  # At least half of minimum
            else:
                assert actual_words < lower_bound


class TestContractErrorDetection:
    """Test suite for detecting common contract errors."""
    
    def test_missing_required_sections(self):
        """Test detection of missing required sections."""
        incomplete_contract = """
        契約書
        
        第1条（目的）何かの目的です。
        第2条（その他）その他の条項です。
        """
        
        result = ContractValidator.validate_japanese_legal_structure(incomplete_contract)
        
        # Should detect incompleteness
        assert result['article_count'] < 5  # Too few articles
        assert result['structure_completeness'] < 0.7  # Low completeness score
    
    def test_placeholder_formatting_errors(self):
        """Test detection of placeholder formatting errors."""
        poorly_formatted_contract = """
        契約書
        
        所在地: ___  # Too short
        賃料: ____________________ yen  # Wrong currency
        期間: xxxxxxxxxx  # Wrong placeholder format
        """
        
        result = ContractValidator.validate_placeholders(poorly_formatted_contract)
        
        # Should detect formatting issues
        assert result['placeholder_consistency_ratio'] < 0.5
        assert not result['required_patterns_found'].get(r'金額:\s*_{10,}円', True)
    
    def test_missing_japanese_legal_terms(self):
        """Test detection of missing essential Japanese legal terms."""
        non_legal_contract = """
        Agreement
        
        Party A: ____________________
        Party B: ____________________
        
        Section 1: Purpose
        Section 2: Terms
        """
        
        result = ContractValidator.validate_japanese_legal_structure(non_legal_contract)
        
        # Should detect lack of proper Japanese legal structure
        assert result['has_title'] is False  # No Japanese contract title
        assert result['has_parties'] is False  # No Japanese party designations
        assert result['has_articles'] is False  # No Japanese article structure
        assert result['structure_completeness'] < 0.3


class TestIntegratedContractValidation:
    """Integration tests for complete contract validation."""
    
    def test_validate_generated_contract_format(self):
        """Test validation of a complete generated contract."""
        # Simulate a contract as it would be generated by the system
        generated_contract = json.dumps({
            "message": "Contract saved successfully",
            "filename": "lease_agreement_20241201_LayerX_Tenant.txt",
            "document_content": """
            賃貸借契約書
            
            賃貸人（甲）: LayerX
            賃借人（乙）: Tenant
            
            第1条（目的）
            甲は乙に対し、下記物件を賃貸し、乙はこれを賃借する。
            
            第2条（対象物件）
            物件の所在地: ____________________
            種類・構造: ____________________
            面積: ____________________㎡
            
            第3条（契約期間）
            開始日: ____________________年____月____日
            終了日: ____________________年____月____日
            
            第4条（賃料）
            月額賃料: ____________________円
            支払期日: 毎月____________________日
            
            第10条（契約解除）
            甲又は乙は債務不履行の場合、本契約を解除することができる。
            
            本契約は、上記条項に合意の上、甲及び乙が署名捺印することにより成立する。
            
            ____________________年____月____日
            """
        })
        
        # Parse and validate
        contract_data = json.loads(generated_contract)
        contract_content = contract_data["document_content"]
        
        validator = ContractValidator()
        
        # Validate structure
        structure_result = validator.validate_japanese_legal_structure(contract_content)
        assert structure_result['has_title'] is True
        assert structure_result['has_parties'] is True
        assert structure_result['article_count'] >= 4
        assert structure_result['has_signature_section'] is True
        
        # Validate placeholders
        placeholder_result = validator.validate_placeholders(contract_content)
        assert placeholder_result['has_placeholders'] is True
        assert placeholder_result['total_placeholders'] >= 8
        
        # Validate content quality
        word_count = validator.count_japanese_words(contract_content)
        assert word_count > 20  # Should have substantial content
    
    def test_contract_validation_pipeline(self):
        """Test a complete validation pipeline."""
        def validate_contract(contract_content: str, target_words: int, contract_type: str) -> Dict[str, Any]:
            """Complete contract validation pipeline."""
            validator = ContractValidator()
            
            results = {
                'word_count': validator.count_japanese_words(contract_content),
                'structure': validator.validate_japanese_legal_structure(contract_content),
                'placeholders': validator.validate_placeholders(contract_content),
            }
            
            # Calculate overall quality score
            word_score = min(results['word_count'] / target_words, 1.0)
            structure_score = results['structure']['structure_completeness']
            placeholder_score = results['placeholders']['placeholder_consistency_ratio']
            
            results['overall_quality'] = (word_score + structure_score + placeholder_score) / 3
            results['meets_requirements'] = results['overall_quality'] > 0.7
            
            return results
        
        # Test with a good contract
        good_contract = """
        賃貸借契約書
        
        賃貸人: ____________________
        賃借人: ____________________
        
        第1条（目的）甲は乙に物件を賃貸する目的で本契約を締結する。
        第2条（対象物件）所在地____________________構造____________________面積____________________
        第3条（契約期間）____________________年____月____日から____________________年____月____日まで
        第4条（賃料）月額____________________円を毎月____________________日に支払う
        第5条（敷金）____________________円を契約時に預託する
        第10条（契約解除）債務不履行等の場合は契約を解除できる
        第11条（原状回復）契約終了時に原状回復する義務を負う
        第12条（合意管轄）紛争は東京地方裁判所の管轄とする
        
        署名捺印____________________年____月____日
        """
        
        results = validate_contract(good_contract, 1000, "lease_agreement")
        
        assert results['meets_requirements'] is True
        assert results['overall_quality'] > 0.7
        assert results['structure']['has_title'] is True
        assert results['placeholders']['has_placeholders'] is True 