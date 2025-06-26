from datetime import datetime
import re

def _sanitize_filename_part(name: str) -> str:
    """
    Sanitizes a string to be suitable for a filename part.
    Replaces non-alphanumeric characters (except underscores and hyphens) with underscores.
    Strips leading/trailing underscores and multiple consecutive underscores.
    """
    sanitized_name = re.sub(r'[^a-zA-Z0-9_-]', '_', name)
    sanitized_name = re.sub(r'_{2,}', '_', sanitized_name)
    sanitized_name = sanitized_name.strip('_')
    return sanitized_name if sanitized_name else "unknown"

def build_lease_agreement_prompt(contract_type: str, number_of_words: int, party_a: str, party_b: str) -> str:
    """
    Constructs a highly detailed Japanese prompt for generating a lease agreement,
    specifying roles, key clauses, placeholders, and meta-instructions for LLM quality and length.

    Args:
        contract_type (str): The type of contract (e.g., "lease_agreement").
        number_of_words (int): The approximate desired word count for the contract.
        party_a (str): The name of Party A (賃貸人 - Lessor).
        party_b (str): The name of Party B (賃借人 - Lessee).

    Returns:
        str: The formatted prompt string for the lease agreement.
    """
    # Calculate bounds for the prompt message
    lower_bound = int(number_of_words * 0.95)
    upper_bound = int(number_of_words * 1.05)

    return (
        f"あなたは日本のトップティアの企業法務弁護士です。この専門知識を活かし、\n"
        f"以下の条件に基づき、日本の法慣習に厳密に準拠した賃貸借契約書を日本語で作成してください。\n"
        f"契約書全体で約 {number_of_words} 語程度の長さでお願いします。\n\n"

        f"**契約作成に関する重要指示:**\n"
        f"* **厳格な語数遵守:** 契約書全体の語数は、指定された約 {number_of_words} 語に対し、**±5%の範囲内（具体的には{lower_bound}語から{upper_bound}語の間）**で厳密に作成してください。この目標語数を満たすために、内容の薄い冗長な表現や無関係な情報を追加したり、必須条項や重要な詳細を省略したりすることは厳禁です。\n"
        f"* **内容の深堀りによる語数調整:** 語数が不足する場合は、各条項の定義を詳細化する、具体的な事例（一般論として）を挙げる、権利義務関係をより精緻に記述する、または標準的な追加条項（例：準拠法、分離可能性、不可抗力など）を適切に含めることで語数を調整してください。ただし、契約の本質を逸脱しないこと。\n"
        f"* **品質と完全性の最優先:** 指定された語数は目安であり、最も重要なのは契約の法的完全性、正確性、および明確性です。語数を満たすために不要な表現や冗長な記述を追加しないでください。逆に、語数が不足しても、必要な法的条項が網羅されていることを優先してください。\n"
        f"* **曖昧さの排除:** 法的文書として曖昧な表現を避け、明確かつ具体的な記述を心がけてください。一般的な表現ではなく、特定の状況に適用可能な文言を使用してください。\n"
        f"* **必須条項の網羅:** 以下の主要条項は必ず含めてください。語数との兼ね合いで省略することは許されません。\n"
        f"* **プレースホルダーの厳守:** 具体的な日付、金額、所在地、特定の詳細情報などは、LLMが具体的な値を生成せず、必ず`____________________`形式のプレースホルダーを維持してください。これはユーザーが後で入力するための領域です。\n\n"

        f"**契約当事者:**\n"
        f"賃貸人: {party_a}\n"
        f"賃借人: {party_b}\n\n"

        f"**必ず含めるべき主要条項と内容の指示:**\n"
        f"1.  **目的（第1条）:** 賃貸人が賃借人に対し、特定の物件を賃貸する旨を明記してください。\n"
        f"2.  **対象物件（第2条）:**\n"
        f"    * 物件の所在地: ____________________\n"
        f"    * 種類・構造: ____________________\n"
        f"    * 面積: ____________________㎡\n"
        f"    * 物件の詳細な特定情報: （例：登記情報、物件番号など、具体例を参考に詳細特定のための記載箇所を設けてください。）\n"
        f"3.  **契約期間（第3条）:**\n"
        f"    * 開始日: ____________________年__月__日\n"
        f"    * 終了日: ____________________年__月__日\n"
        f"    * 契約期間は明確に記述してください。具体的な日付はユーザーが入力するため、プレースホルダーを維持してください。\n"
        f"4.  **賃料（第4条）:**\n"
        f"    * 月額賃料: ____________________円\n"
        f"    * 支払期日: 毎月____________________日\n"
        f"    * 支払方法: 賃貸人が指定する銀行口座への振込を原則とする旨。\n"
        f"5.  **敷金・保証金（第5条、任意）:** 敷金または保証金の有無、金額、返還条件について記述してください。不要な場合は「該当なし」と明記してください。\n"
        f"6.  **管理費・共益費（第6条、任意）:** 管理費や共益費の有無、金額、支払方法について記述してください。不要な場合は「該当なし」と明記してください。\n"
        f"7.  **使用目的（第7条）:** 住居用、事業用など、物件の使用目的を具体的に記述してください。\n"
        f"8.  **禁止事項（第8条）:** 無断転貸、増改築の禁止など、賃借人が遵守すべき事項を記述してください。\n"
        f"9.  **修繕義務（第9条）:** 物件の修繕義務の所在（賃貸人、賃借人）について記述してください。\n"
        f"10. **契約解除（第10条）:**\n"
        f"    * 解除の要件: 債務不履行、目的外使用など、契約解除に至る条件を具体的に記述してください。\n"
        f"    * 通知期間: 契約解除の意思表示は、原則として____________________ヶ月前までに書面で行うものとします。\n"
        f"11. **原状回復義務（第11条）:** 契約終了時の原状回復義務について記述してください。\n"
        f"12. **合意管轄（第12条）:** 本契約に関する紛争の解決に関する合意管轄裁判所を記述してください。\n\n"

        f"**最終書式に関する指示:**\n"
        f"* 日本の一般的なビジネス契約書のフォーマット（例：契約書名、契約締結日、当事者の表示、各条項、署名欄）に厳密に準拠してください。\n"
        f"* 具体的な日付、金額、所在地などの情報はプレースホルダー（例：`____________________`）の形式で記述し、LLMが具体的な値を生成しないようにしてください。\n"
        f"* 句読点や改行を適切に使用し、読みやすい契約書を作成してください。\n"
        f"* 法的専門用語を正確に使用してください。\n"
        f"* 契約書の最後に、賃貸人、賃借人の署名欄と、契約締結日を「本契約は、上記条項に合意の上、賃貸人及び賃借人が署名捺印することにより成立する。」という文言と共に設けてください。\n\n"

        f"生成後は、提供されている保存ツールを使ってローカルディスクに保存してください。"
    )

def build_outsourcing_contract_prompt(contract_type: str, number_of_words: int, party_a: str, party_b: str) -> str:
    """
    Constructs a highly detailed Japanese prompt for generating an outsourcing contract,
    specifying roles, key clauses, placeholders, and meta-instructions for LLM quality and length.

    Args:
        contract_type (str): The type of contract (e.g., "outsourcing_contract").
        number_of_words (int): The approximate desired word count for the contract.
        party_a (str): The name of Party A (委託者 - Client).
        party_b (str): The name of Party B (受託者 - Contractor).

    Returns:
        str: The formatted prompt string for the outsourcing contract.
    """
    # Calculate bounds for the prompt message
    lower_bound = int(number_of_words * 0.95)
    upper_bound = int(number_of_words * 1.05)

    return (
        f"あなたは日本のトップティアの企業法務弁護士です。この専門知識を活かし、\n"
        f"以下の条件に基づき、日本の法慣習に厳密に準拠した業務委託契約書を日本語で作成してください。\n"
        f"契約書全体で約 {number_of_words} 語程度の長さでお願いします。\n\n"

        f"**契約作成に関する重要指示:**\n"
        f"* **厳格な語数遵守:** 契約書全体の語数は、指定された約 {number_of_words} 語に対し、**±5%の範囲内（具体的には{lower_bound}語から{upper_bound}語の間）**で厳密に作成してください。この目標語数を満たすために、内容の薄い冗長な表現や無関係な情報を追加したり、必須条項や重要な詳細を省略したりすることは厳禁です。\n"
        f"* **内容の深堀りによる語数調整:** 語数が不足する場合は、各条項の定義を詳細化する、具体的な事例（一般論として）を挙げる、権利義務関係をより精緻に記述する、または標準的な追加条項（例：準拠法、分離可能性、不可抗力など）を適切に含めることで語数を調整してください。ただし、契約の本質を逸脱しないこと。\n"
        f"* **品質と完全性の最優先:** 指定された語数は目安であり、最も重要なのは契約の法的完全性、正確性、および明確性です。語数を満たすために不要な表現や冗長な記述を追加しないでください。逆に、語数が不足しても、必要な法的条項が網羅されていることを優先してください。\n"
        f"* **曖昧さの排除:** 法的文書として曖昧な表現を避け、明確かつ具体的な記述を心がけてください。一般的な表現ではなく、特定の状況に適用可能な文言を使用してください。\n"
        f"* **必須条項の網羅:** 以下の主要条項は必ず含めてください。語数との兼ね合いで省略することは許されません。\n"
        f"* **プレースホルダーの厳守:** 具体的な日付、金額、業務内容、特定の詳細情報などは、LLMが具体的な値を生成せず、必ず`____________________`形式のプレースホルダーを維持してください。これはユーザーが後で入力するための領域です。\n\n"

        f"**契約当事者:**\n"
        f"委託者: {party_a}\n"
        f"受託者: {party_b}\n\n"

        f"**必ず含めるべき主要条項と内容の指示:**\n"
        f"1.  **目的（第1条）:** 委託者が受託者に対し、特定の業務を委託する旨を明記してください。\n"
        f"2.  **委託業務の内容（第2条）:**\n"
        f"    * 業務の具体的な範囲と詳細: ____________________\n"
        f"    * 成果物の特定: ____________________（例：報告書、システム、デザインなど、具体例を参考に詳細特定のための記載箇所を設けてください。）\n"
        f"3.  **委託期間（第3条）:**\n"
        f"    * 開始日: ____________________年__月__日\n"
        f"    * 終了日: ____________________年__月__日\n"
        f"    * 委託期間は明確に記述してください。具体的な日付はユーザーが入力するため、プレースホルダーを維持してください。\n"
        f"4.  **報酬（第4条）:**\n"
        f"    * 委託報酬: ____________________円\n"
        f"    * 支払期日: 毎月____________________日\n"
        f"    * 支払方法: 受託者が指定する銀行口座への振込を原則とする旨。\n"
        f"5.  **費用負担（第5条、任意）:** 業務遂行に必要な費用の負担について記述してください。不要な場合は「原則、報酬に含む」などと明記してください。\n"
        f"6.  **知的財産権の帰属（第6条）:** 業務遂行により生じる成果物の知的財産権の帰属について明確に記述してください。\n"
        f"7.  **秘密保持義務（第7条）:** 業務を通じて知り得た秘密情報の取り扱いについて記述してください。\n"
        f"8.  **再委託（第8条）:** 受託者が業務を第三者に再委託する際の条件について記述してください。\n"
        f"9.  **契約解除（第9条）:**\n"
        f"    * 解除の要件: 債務不履行、重大な過失など、契約解除に至る条件を具体的に記述してください。\n"
        f"    * 通知期間: 契約解除の意思表示は、原則として____________________ヶ月前までに書面で行うものとします。\n"
        f"10. **損害賠償（第10条）:** 本契約に違反した場合の損害賠償について記述してください。\n"
        f"11. **反社会的勢力の排除（第11条）:** 反社会的勢力との関係がないことを表明し保証する条項を記述してください。\n"
        f"12. **合意管轄（第12条）:** 本契約に関する紛争の解決に関する合意管轄裁判所を記述してください。\n\n"

        f"**最終書式に関する指示:**\n"
        f"* 日本の一般的なビジネス契約書のフォーマット（例：契約書名、契約締結日、当事者の表示、各条項、署名欄）に厳密に準拠してください。\n"
        f"* 具体的な日付、金額、業務内容などの情報はプレースホルダー（例：`____________________`）の形式で記述し、LLMが具体的な値を生成しないようにしてください。\n"
        f"* 句読点や改行を適切に使用し、読みやすい契約書を作成してください。\n"
        f"* 法的専門用語を正確に使用してください。\n"
        f"* 契約書の最後に、委託者、受託者の署名欄と、契約締結日を「本契約は、上記条項に合意の上、委託者及び受託者が署名捺印することにより成立する。」という文言と共に設けてください。\n\n"

        f"生成後は、提供されている保存ツールを使ってローカルディスクに保存してください。"
    )

def build_filename(contract_type: str, number_of_words: int, party_a: str, party_b: str) -> str:
    """
    Generates a standardized and sanitized filename for the contract.
    The filename includes the contract type, current date, and sanitized names of the parties.
    Example: lease_agreement_YYYYMMDD_Party_A_Party_B.txt
    """
    date_str = datetime.now().strftime("%Y%m%d")
    
    # Sanitize party names for the filename
    sanitized_party_a = _sanitize_filename_part(party_a)
    sanitized_party_b = _sanitize_filename_part(party_b)

    return f"{contract_type}_{date_str}_{sanitized_party_a}_{sanitized_party_b}.txt"