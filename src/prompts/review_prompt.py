"""
Contract Review Prompts for Japanese Business Contracts
This module contains prompts for reviewing and analyzing Japanese business contracts.
"""

def get_contract_review_prompt(contract_content: str, filename: str) -> str:
    """
    Generate a comprehensive review prompt for Japanese business contracts.
    
    Args:
        contract_content (str): The content of the contract to review
        filename (str): The name of the contract file being reviewed
        
    Returns:
        str: A detailed prompt for contract review
    """
    
    return f"""あなたは日本の法務に精通した契約書レビューの専門家です。以下の契約書を詳細に分析し、包括的なレビューを提供してください。

契約書ファイル名: {filename}

契約書内容:
{contract_content}

以下の観点から契約書を分析してください：

## 1. 契約書の基本情報
- 契約の種類と目的
- 契約当事者の確認
- 契約期間と有効期限
- 主要な権利義務関係

## 2. 法的リスク分析
- 法的に問題となる可能性のある条項
- 不明確または曖昧な表現
- 一方当事者に不利な条項
- 法令違反の可能性

## 3. 契約条項の妥当性
- 各条項の合理性
- 業界標準との比較
- バランスの取れた条項構成
- 必要な条項の不足

## 4. 改善提案
- 具体的な修正案
- 追加すべき条項
- 削除または変更すべき条項
- リスク軽減のための提案

## 5. 総合評価
- 契約書の全体的な品質
- 実務上の使いやすさ
- 法的安全性の評価
- 推奨される対応

レビュー結果は以下の形式で出力してください：

【契約書レビュー報告書】

**契約書名**: {filename}
**レビュー日**: [現在の日付]

**1. 基本情報**
[契約の基本情報を記載]

**2. 発見された問題点**
[問題点を優先度順に列挙]

**3. 法的リスク**
[高リスク、中リスク、低リスクに分類]

**4. 改善提案**
[具体的な修正案と理由]

**5. 総合評価**
[A〜Dの4段階評価と理由]

**6. 推奨アクション**
[次に取るべき具体的な行動]

専門的で実用的なレビューを提供し、契約当事者が適切な判断を下せるよう支援してください。"""

def get_contract_summary_prompt(contract_content: str, filename: str) -> str:
    """
    Generate a prompt for creating a contract summary.
    
    Args:
        contract_content (str): The content of the contract to summarize
        filename (str): The name of the contract file
        
    Returns:
        str: A prompt for contract summarization
    """
    
    return f"""以下の契約書の要点を簡潔にまとめてください。

契約書ファイル名: {filename}

契約書内容:
{contract_content}

以下の形式で要約してください：

【契約書要約】

**契約書名**: {filename}
**契約種別**: [契約の種類]
**当事者**: [甲乙の名称]
**契約期間**: [開始日〜終了日]
**主要な内容**: 
- [重要なポイント1]
- [重要なポイント2]
- [重要なポイント3]

**注意事項**: [特に注意すべき条項や制限事項]
**更新・解約**: [更新条件や解約条件]

簡潔で分かりやすい要約を作成してください。"""

def get_risk_analysis_prompt(contract_content: str, filename: str) -> str:
    """
    Generate a prompt focused specifically on risk analysis.
    
    Args:
        contract_content (str): The content of the contract to analyze
        filename (str): The name of the contract file
        
    Returns:
        str: A prompt for risk analysis
    """
    
    return f"""以下の契約書について、法的リスクを中心とした分析を行ってください。

契約書ファイル名: {filename}

契約書内容:
{contract_content}

以下の観点からリスクを分析してください：

## リスク分析

### 高リスク（即座に対応が必要）
- [重大な法的問題や不利な条項]

### 中リスク（検討・交渉が推奨）
- [改善の余地がある条項]

### 低リスク（将来的に検討）
- [軽微な改善点]

### 推奨対応策
- [各リスクに対する具体的な対応方法]

リスクの優先順位を明確にし、実践的な対応策を提示してください。""" 