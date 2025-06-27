from datetime import datetime
import re

def _sanitize_filename_part(name: str) -> str:
    """
    Sanitizes a string to be suitable for a filename part.
    Preserves Japanese characters and alphanumeric characters.
    Replaces unsafe filename characters with underscores.
    """
    # Remove only characters that are problematic for filenames
    # Keep: alphanumeric, Japanese characters, underscores, hyphens
    sanitized_name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', name)
    sanitized_name = re.sub(r'_{2,}', '_', sanitized_name)
    sanitized_name = sanitized_name.strip('_')
    return sanitized_name if sanitized_name else "unknown"

def build_lease_agreement_prompt(contract_type: str, number_of_words: int, party_a: str, party_b: str, folder_to_save: str) -> str:
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
    lower_bound = int(number_of_words * 0.95)
    upper_bound = int(number_of_words * 1.05)

    return (
        f"あなたは日本のトップティアの企業法務弁護士です。**日本の民法、借地借家法、その他関連法令に精通し、**\n" # Added specific Japanese laws
        f"その専門知識を活かし、以下の条件に基づき、日本の法慣習に厳密に準拠した賃貸借契約書を日本語で作成してください。\n"
        f"契約書全体で約 {number_of_words} 語程度の**長さを目安とします。**\n\n" # Softened the word count instruction to "目安とします" (as a guideline)

        f"**【契約作成に関する重要指示】**\n" # Improved heading for emphasis
        f"* **法的な正確性と完全性の最優先:** 指定された語数は、契約の網羅性と詳細度を確保するための目安です。**最も重要なのは、契約の法的完全性、正確性、および明確性です。**語数を満たすために内容の薄い冗長な表現や無関係な情報を追加したり、必須条項や重要な詳細を省略したりすることは厳禁です。\n"
        f"* **内容の深掘りによる語数調整:** 語数が不足する場合は、以下の観点から各条項の記述を詳細化または追加条項を検討してください。\n"
        f"    * 各条項の定義を詳細化する。\n"
        f"    * 具体的な適用事例や解釈基準（一般論として）を明記する。\n"
        f"    * 賃貸人および賃借人の権利義務関係をより精緻に記述する。\n"
        f"    * 標準的な追加条項（例：準拠法、分離可能性、不可抗力、**暴力団等反社会的勢力の排除**、協議解決、通知方法、合意管轄、契約締結費用負担など）を適切に含める。\n" # Added anti-social forces clause and other common clauses
        f"    * 特に、賃貸物件の**附属設備に関する詳細**（例：エアコン、給湯器の有無、保守責任の所在）、**共用部分の使用に関する細則**、**賃料改定に関する条項**（協議条項、鑑定評価に基づく改定など）、**更新料の有無**、**損害賠償額の予定**、**遅延損害金利率**など、賃貸借契約に特有の詳細を網羅してください。\n" # Added specific lease-related details for expansion
        f"* **厳格な語数遵守の目安:** 契約書全体の語数は、指定された約 {number_of_words} 語に対し、**±5%の範囲内（具体的には{lower_bound}語から{upper_bound}語の間）**に収まるよう、上記「内容の深掘り」指示に基づき調整してください。\n" # Reordered to prioritize quality, then word count
        f"* **曖昧さの排除:** 法的文書として曖昧な表現を避け、明確かつ具体的な記述を心がけてください。一般的な表現ではなく、特定の状況に適用可能な文言を使用し、誤解の余地がないようにしてください。\n"
        f"* **必須条項の網羅:** 後述の主要条項は必ず含めてください。語数との兼ね合いで省略することは許されません。\n"
        f"* **プレースホルダーの厳守:** 具体的な日付、金額、所在地、特定の詳細情報などは、LLMが具体的な値を生成せず、必ず`____________________`形式のプレースホルダーを維持してください。これはユーザーが後で入力するための領域です。\n\n"

        f"**【契約当事者】**\n"
        f"賃貸人: {party_a}\n"
        f"賃借人: {party_b}\n\n"

        f"**【必ず含めるべき主要条項と内容の指示】**\n" # Improved heading
        f"1.  **目的（第1条）:** 賃貸人が賃借人に対し、特定の物件を賃貸する旨を明確に規定してください。\n"
        f"2.  **対象物件（第2条）:**\n"
        f"    * 物件の所在地: ____________________\n"
        f"    * 種類・構造: ____________________\n"
        f"    * 面積: ____________________㎡\n"
        f"    * 物件の詳細な特定情報: （例：登記情報、物件番号、名称など、物件を一意に特定できる情報を記載するプレースホルダーを設けてください。）\n"
        f"    * **付属設備:** （例：エアコン、給湯器等の有無と保守責任の所在、ユーザーが入力するプレースホルダーを設けてください。）\n" # Added specific detail
        f"3.  **契約期間（第3条）:**\n"
        f"    * 開始日: ____________________年__月__日\n"
        f"    * 終了日: ____________________年__月__日\n"
        f"    * 契約期間は明確に記述し、期間満了後の**更新に関する規定**（合意更新の原則、法定更新の適用除外など）も考慮したプレースホルダーを設けてください。\n" # Added update clause consideration
        f"4.  **賃料（第4条）:**\n"
        f"    * 月額賃料: ____________________円\n"
        f"    * 支払期日: 毎月____________________日\n"
        f"    * 支払方法: 賃貸人が指定する銀行口座への振込を原則とする旨。**振込手数料の負担についても明記してください。**\n" # Added fee detail
        f"    * **賃料の改定:** 経済情勢の変化や固定資産税等の増減に応じた賃料改定の可能性とその手続き（協議、調停、裁判など）に関する条項を設けてください。\n" # Added rent revision
        f"5.  **敷金・保証金（第5条、任意）:** 敷金または保証金の有無、金額、預託方法、運用、**返還条件（償却、現状回復費用控除など）**について詳細に記述してください。不要な場合は「該当なし」と明記してください。\n" # Added detail on return conditions
        f"6.  **管理費・共益費（第6条、任意）:** 管理費や共益費の有無、金額、支払方法、**使途**について記述してください。不要な場合は「該当なし」と明記してください。\n" # Added purpose of use
        f"7.  **使用目的（第7条）:** 住居用、事業用、または特定の用途（例：店舗、事務所）など、物件の使用目的を具体的に記述し、**目的外使用の禁止に関する条項**を含めてください。\n" # Emphasized prohibition of unintended use
        f"8.  **禁止事項（第8条）:** 無断転貸、増改築、物件の現状変更、危険物の持ち込み、騒音発生など、賃借人が遵守すべき事項を詳細に記述してください。特に、**ペット飼育や楽器演奏に関する規定**も考慮してください（任意）。\n" # Added more specific examples for prohibitions
        f"9.  **修繕義務（第9条）:** 物件の修繕義務の所在（賃貸人、賃借人）およびその範囲、費用負担、通知義務について詳細に記述してください。**通常損耗、経年劣化、賃借人の故意・過失による損傷の場合分けを明確にしてください。**\n" # Added detailed repair conditions
        f"10. **契約解除（第10条）:**\n"
        f"    * 解除の要件: 債務不履行（特に賃料滞納）、目的外使用、禁止事項違反、破産手続開始、差押えなど、契約解除に至る具体的な条件を記述してください。\n"
        f"    * 通知期間: 契約解除の意思表示は、原則として____________________ヶ月前までに書面で行うものとします。\n"
        f"    * **催告の有無:** 催告の有無やその期間についても明確にしてください。\n" # Added for clarity on termination
        f"11. **原状回復義務（第11条）:** 契約終了時の原状回復義務、**特約による通常の損耗・経年劣化の負担、残置物の取り扱い、費用負担**について詳細に記述してください。\n" # Added detail on restoration
        f"12. **合意管轄（第12条）:** 本契約に関する紛争の解決に関する合意管轄裁判所を記述してください。**複数の裁判所を指定する場合や、調停前置主義を定める場合も考慮してください。**\n" # Added options for jurisdiction
        f"13. **反社会的勢力の排除（第13条）：** 賃貸人、賃借人双方が反社会的勢力ではないことを表明し保証する条項を必ず含めてください。\n" # CRITICAL new clause
        f"14. **特約事項（第14条、任意）：** 上記以外に、個別具体的な事情に応じた特約事項を設けるためのプレースホルダーを含めてください。\n\n" # Added for custom clauses

        f"**【最終書式に関する指示】**\n" # Improved heading
        f"* 日本の一般的なビジネス契約書のフォーマット（例：契約書名、契約締結日、当事者の表示、各条項、署名欄、**別紙の有無**）に厳密に準拠してください。\n" # Added consideration for appendices
        f"* 具体的な日付、金額、所在地、期間、業務内容などの情報はプレースホルダー（例：`____________________`）の形式で記述し、LLMが具体的な値を生成しないようにしてください。\n"
        f"* 句読点や改行を適切に使用し、読みやすい契約書を作成してください。\n"
        f"* 法的専門用語を正確に使用し、**文体は硬質かつ客観的であること。条文ごとに見出しを付し、番号を付与してください。**\n" # Emphasized legal style guidance
        f"* 契約書の最後に、賃貸人、賃借人の署名欄と、契約締結日を「本契約は、上記条項に合意の上、賃貸人及び賃借人が署名捺印することにより成立する。」という文言と共に設けてください。\n\n"

        f"生成後は、提供されている保存ツールを使ってローカルディスクに保存してください。"
    )

def build_outsourcing_contract_prompt(contract_type: str, number_of_words: int, party_a: str, party_b: str, folder_to_save: str) -> str:
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
    lower_bound = int(number_of_words * 0.95)
    upper_bound = int(number_of_words * 1.05)

    return (
        f"あなたは日本のトップティアの企業法務弁護士です。**日本の民法、下請法（該当する場合）、個人情報保護法、その他関連法令に精通し、**\n" # Added specific Japanese laws
        f"その専門知識を活かし、以下の条件に基づき、日本の法慣習に厳密に準拠した業務委託契約書を日本語で作成してください。\n"
        f"契約書全体で約 {number_of_words} 語程度の**長さを目安とします。**\n\n" # Softened the word count instruction

        f"**【契約作成に関する重要指示】**\n"
        f"* **法的な正確性と完全性の最優先:** 指定された語数は、契約の網羅性と詳細度を確保するための目安です。**最も重要なのは、契約の法的完全性、正確性、および明確性です。**語数を満たすために内容の薄い冗長な表現や無関係な情報を追加したり、必須条項や重要な詳細を省略したりすることは厳禁です。\n"
        f"* **内容の深掘りによる語数調整:** 語数が不足する場合は、以下の観点から各条項の記述を詳細化または追加条項を検討してください。\n"
        f"    * 各条項の定義を詳細化する。\n"
        f"    * 具体的な適用事例や解釈基準（一般論として）を明記する。\n"
        f"    * 委託者および受託者の権利義務関係をより精緻に記述する。\n"
        f"    * 標準的な追加条項（例：準拠法、分離可能性、不可抗力、**暴力団等反社会的勢力の排除**、協議解決、通知方法、合意管轄、契約締結費用負担など）を適切に含める。\n" # Added anti-social forces clause and other common clauses
        f"    * 特に、**業務の検収基準とプロセス**、**瑕疵担保責任（契約不適合責任）の範囲と期間**、**納期遅延に関する違約金**、**報告義務の頻度と内容**、**秘密情報の定義と例外**、**データセキュリティに関する条項**、**監査権**など、業務委託契約に特有の詳細を網羅してください。\n" # Added specific outsourcing details for expansion
        f"* **厳格な語数遵守の目安:** 契約書全体の語数は、指定された約 {number_of_words} 語に対し、**±5%の範囲内（具体的には{lower_bound}語から{upper_bound}語の間）**に収まるよう、上記「内容の深掘り」指示に基づき調整してください。\n" # Reordered
        f"* **曖昧さの排除:** 法的文書として曖昧な表現を避け、明確かつ具体的な記述を心がけてください。一般的な表現ではなく、特定の状況に適用可能な文言を使用し、誤解の余地がないようにしてください。\n"
        f"* **必須条項の網羅:** 後述の主要条項は必ず含めてください。語数との兼ね合いで省略することは許されません。\n"
        f"* **プレースホルダーの厳守:** 具体的な日付、金額、業務内容、特定の詳細情報などは、LLMが具体的な値を生成せず、必ず`____________________`形式のプレースホルダーを維持してください。これはユーザーが後で入力するための領域です。\n\n"

        f"**【契約当事者】**\n"
        f"委託者: {party_a}\n"
        f"受託者: {party_b}\n\n"

        f"**【必ず含めるべき主要条項と内容の指示】**\n"
        f"1.  **目的（第1条）:** 委託者が受託者に対し、特定の業務を委託する旨を明確に規定してください。\n"
        f"2.  **委託業務の内容（第2条）:**\n"
        f"    * 業務の具体的な範囲と詳細: ____________________\n"
        f"    * 成果物の特定: ____________________（例：報告書、システム、デザインなど、具体例を参考に詳細特定のための記載箇所を設けてください。）\n"
        f"    * **業務の遂行方法および進捗報告義務**：受託者の業務遂行方法、定期的な進捗報告の頻度と内容、会議の設定などに関する条項を設けてください。\n" # Added specific for task execution
        f"    * **検収基準とプロセス:** 成果物の検収方法、期間、基準、瑕疵があった場合の対応（修補、代替、減額など）について具体的に記述してください。\n" # Added acceptance criteria
        f"3.  **委託期間（第3条）:**\n"
        f"    * 開始日: ____________________年__月__日\n"
        f"    * 終了日: ____________________年__月__日\n"
        f"    * 委託期間は明確に記述してください。具体的な日付はユーザーが入力するため、プレースホルダーを維持してください。**期間満了後の更新の有無や条件についても考慮してください。**\n" # Added for update consideration
        f"4.  **報酬（第4条）:**\n"
        f"    * 委託報酬: ____________________円\n"
        f"    * 支払期日: 毎月____________________日\n"
        f"    * 支払方法: 受託者が指定する銀行口座への振込を原則とする旨。**振込手数料の負担についても明記してください。**\n" # Added fee detail
        f"    * **報酬の改定:** 業務内容の変更や期間延長に伴う報酬の改定に関する条項を設けてください（任意）。\n" # Added for fee revision
        f"5.  **費用負担（第5条、任意）:** 業務遂行に必要な費用の負担について記述してください。**出張費、資料作成費、システム利用料など具体例を挙げ、原則として報酬に含むか、実費精算とするか明記してください。**不要な場合は「原則、報酬に含む」などと明記してください。\n" # Added details for cost burden
        f"6.  **知的財産権の帰属（第6条）:** 業務遂行により生じる成果物の知的財産権（著作権、特許権など）の帰属、利用許諾、二次利用に関する条件を明確に記述してください。\n"
        f"7.  **秘密保持義務（第7条）:** 業務を通じて知り得た秘密情報の定義、範囲、使用目的の制限、管理方法、返還・廃棄義務、違反した場合の措置について詳細に記述してください。\n"
        f"8.  **再委託（第8条）:** 受託者が業務を第三者に再委託する際の条件（委託者の事前の書面承諾、再委託先の管理責任、再委託先に対する本契約の義務遵守の徹底など）について記述してください。\n"
        f"9.  **契約解除（第9条）:**\n"
        f"    * 解除の要件: 債務不履行、重大な過失、**信義則違反**、破産手続開始、差押えなど、契約解除に至る具体的な条件を記述してください。\n" # Added "信義則違反" (breach of good faith)
        f"    * 通知期間: 契約解除の意思表示は、原則として____________________ヶ月前までに書面で行うものとします。\n"
        f"    * **催告の有無:** 催告の有無やその期間についても明確にしてください。\n" # Added for clarity on termination
        f"10. **損害賠償（第10条）:** 本契約に違反した場合の損害賠償の範囲（直接損害、間接損害）、上限額、遅延損害金利率について記述してください。\n"
        f"11. **反社会的勢力の排除（第11条）：** 委託者、受託者双方が反社会的勢力ではないことを表明し保証する条項を必ず含めてください。\n" # CRITICAL new clause
        f"12. **合意管轄（第12条）:** 本契約に関する紛争の解決に関する合意管轄裁判所を記述してください。**複数の裁判所を指定する場合や、調停前置主義を定める場合も考慮してください。**\n" # Added options for jurisdiction
        f"13. **個人情報保護（第13条、任意）：** 個人情報を取り扱う業務の場合、個人情報の安全管理措置、目的外利用の禁止、委託元への報告義務など、個人情報保護法に準拠した条項を設けてください。\n" # Added for data privacy
        f"14. **特約事項（第14条、任意）：** 上記以外に、個別具体的な事情に応じた特約事項を設けるためのプレースホルダーを含めてください。\n\n"

        f"**【最終書式に関する指示】**\n"
        f"* 日本の一般的なビジネス契約書のフォーマット（例：契約書名、契約締結日、当事者の表示、各条項、署名欄、**別紙の有無**）に厳密に準拠してください。\n" # Added consideration for appendices
        f"* 具体的な日付、金額、業務内容などの情報はプレースホルダー（例：`____________________`）の形式で記述し、LLMが具体的な値を生成しないようにしてください。\n"
        f"* 句読点や改行を適切に使用し、読みやすい契約書を作成してください。\n"
        f"* 法的専門用語を正確に使用し、**文体は硬質かつ客観的であること。条文ごとに見出しを付し、番号を付与してください。**\n" # Emphasized legal style guidance
        f"* 契約書の最後に、委託者、受託者の署名欄と、契約締結日を「本契約は、上記条項に合意の上、委託者及び受託者が署名捺印することにより成立する。」という文言と共に設けてください。\n\n"

        f"生成後は、提供されている保存ツールを使ってローカルディスクに保存してください。"
    )

def build_filename(contract_type: str, number_of_words: int, party_a: str, party_b: str, folder_to_save: str) -> str:
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