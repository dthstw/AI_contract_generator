import os
from agents import function_tool

# Save document tool
@function_tool
def save_str_to_disc(document: str, filename: str, directory: str = "contracts") -> str:
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, filename)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(document) 
        
    return f"Contract saved to: {path}"