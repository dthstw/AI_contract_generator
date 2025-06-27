#searches txt files in a folder to find a specific string

import os

def search_txt_files(folder_path: str, search_string: str) -> str:
    """
    Searches for a specific string in all .txt files within a given folder.
    
    Args:
        folder_path (str): The path to the folder containing the .txt files.
        search_string (str): The string to search for in the .txt files.
        
    """
    results = []
    for file in os.listdir(folder_path):
        if file.endswith(".txt"):
            with open(os.path.join(folder_path, file), "r", encoding="utf-8") as f:
                if search_string in f.read():
                    results.append(file)
    return results