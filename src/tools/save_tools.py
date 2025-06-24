import os
from agents import function_tool
import json

def get_unique_filename(base: str, ext: str, directory: str) -> str:
    """
    Generate a unique file path by appending an incremental index if needed.
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
def save_str_to_disc(document: str, filename: str, directory: str = "contracts") -> dict:
    """
    Save the document string to a uniquely named file in the given directory.
    Returns a dictionary with filename, path, and a message.
    """
    base, ext = os.path.splitext(filename)
    path = get_unique_filename(base, ext, directory)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(document)

    final_name = os.path.basename(path)
    
    return json.dumps({
    "filename": final_name,
    "path": path,
    "message": f"✅ Contract saved in `{directory}` as `{final_name}`"
    }, ensure_ascii=False)

