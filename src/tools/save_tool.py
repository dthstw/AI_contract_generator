import os
from agents import function_tool
import json
from langfuse import observe

def get_unique_filename(base: str, ext: str, directory: str) -> str:
    """
    Generate a unique file path by appending an incremental index if needed.
    Ensures that the file does not overwrite an existing one by adding a counter.

    Args:
        base (str): The base name of the file (without extension).
        ext (str): The file extension (e.g., ".txt", ".json").
        directory (str): The directory where the file is intended to be saved.

    Returns:
        str: A unique file path that does not currently exist.
    """
    ext = ext if ext else ".txt"
    base = base.rstrip('.')  # Avoid double dots like 'file..txt'

    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, f"{base}{ext}")
    
    if not os.path.exists(path):
        return path

    counter = 1
    while True:
        alt_name = f"{base}_{counter:03d}{ext}"
        alt_path = os.path.join(directory, alt_name)
        if not os.path.exists(alt_path):
            return alt_path
        counter += 1

@function_tool
@observe
def save_str_to_disc(document: str, filename: str, directory: str = "contracts") -> dict:
    """
    Save the document string to a uniquely named file in the given directory.
    This function generates a unique filename to prevent overwriting existing files.

    Args:
        document (str): The string content to be saved to the file.
        filename (str): The desired base filename (e.g., "my_contract.txt").
        directory (str, optional): The directory where the file will be saved.
                                   Defaults to "contracts".

    Returns:
        dict: A dictionary containing the final filename, the full path to the file,
              and a success message.
    """
    base, ext = os.path.splitext(filename)
    os.makedirs(directory, exist_ok=True)
    path = get_unique_filename(base, ext, directory)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(document)

    final_name = os.path.basename(path)
    
    return json.dumps({
        "filename": final_name,
        "path": path,
        "message": f"Contract saved in `{directory}` as `{final_name}`"
    }, ensure_ascii=False)