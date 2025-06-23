from datetime import datetime

#Prompt constructor
def build_lease_agreement_prompt(number_of_words: int, party_a: str, party_b: str) -> str:
    return (
        f"Generate an English lease agreement contract with approximately {number_of_words} words.\n"
        f"Party A: {party_a}\nParty B: {party_b}\n"
        f"After generating, save it to the local disc using the available tool."
    )
    
def build_outsourcing_contract_prompt(number_of_words: int, party_a: str, party_b: str) -> str:
    return (
        f"Generate an English outsorcing contract with approximately {number_of_words} words.\n"
        f"Party A: {party_a}\nParty B: {party_b}\n"
        f"After generating, save it to the local disc using the available tool."
    )

# Filename generation
def build_filename(contract_type: str, party_a: str, party_b: str) -> str:
    date_str = datetime.now().strftime("%Y%m%d")
    return f"{contract_type}_{date_str}_{party_a}_{party_b}.txt"