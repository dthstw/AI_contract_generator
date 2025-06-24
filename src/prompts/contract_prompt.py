from datetime import datetime

#Prompt constructor
def build_lease_agreement_prompt(contract_type: str, number_of_words: int, party_a: str, party_b: str) -> str:
    return (
        f"{party_a} と {party_b} の間で締結される賃貸借契約書を作成してください。\n"
        f"契約書は日本語で、全体で約 {number_of_words} 語程度の長さとしてください。\n"
        f"形式は日本の一般的なビジネス契約書のスタイルに準拠し、必要な条項（目的、契約期間、賃料、解約条件など）を含めてください。\n"
        f"生成後は、提供されている保存ツールを使ってローカルディスクに保存してください。"
    )
    
def build_outsourcing_contract_prompt(contract_type: str, number_of_words: int, party_a: str, party_b: str) -> str:
    return (
        f"{party_a} と {party_b} の間で締結される業務委託契約書を作成してください。\n"
        f"契約書は日本語で、全体で約 {number_of_words} 語程度の長さとしてください。\n"
        f"形式は日本の標準的なビジネス契約書に準拠し、業務範囲、委託期間、報酬、秘密保持義務、契約解除に関する条項を含めてください。\n"
        f"生成後は、提供されている保存ツールを使ってローカルディスクに保存してください。"
    )

# Filename generation
def build_filename(contract_type: str, number_of_words: int, party_a: str, party_b: str) -> str:
    date_str = datetime.now().strftime("%Y%m%d")
    return f"{contract_type}_{date_str}_{party_a}_{party_b}.txt"