import os
from agents import function_tool
import json
from langfuse import observe

@function_tool
@observe
def read_contract_file(file_path: str) -> dict:
    """
    Read a contract file from the specified path and return its content.
    This function reads text files (typically contracts) and returns the content
    for analysis or review purposes.

    Args:
        file_path (str): The path to the contract file to be read.

    Returns:
        dict: A dictionary containing the file content, filename, and status.
    """
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            return json.dumps({
                "success": False,
                "error": f"File not found: {file_path}",
                "content": "",
                "filename": ""
            }, ensure_ascii=False)
        
        # Check if it's a file (not directory)
        if not os.path.isfile(file_path):
            return json.dumps({
                "success": False,
                "error": f"Path is not a file: {file_path}",
                "content": "",
                "filename": ""
            }, ensure_ascii=False)
        
        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        filename = os.path.basename(file_path)
        
        return json.dumps({
            "success": True,
            "content": content,
            "filename": filename,
            "file_path": file_path,
            "message": f"Successfully read contract file: {filename}"
        }, ensure_ascii=False)
        
    except UnicodeDecodeError:
        return json.dumps({
            "success": False,
            "error": f"Unable to read file as UTF-8: {file_path}. Please ensure the file contains text.",
            "content": "",
            "filename": os.path.basename(file_path) if os.path.exists(file_path) else ""
        }, ensure_ascii=False)
        
    except PermissionError:
        return json.dumps({
            "success": False,
            "error": f"Permission denied reading file: {file_path}",
            "content": "",
            "filename": os.path.basename(file_path) if os.path.exists(file_path) else ""
        }, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Unexpected error reading file: {str(e)}",
            "content": "",
            "filename": os.path.basename(file_path) if os.path.exists(file_path) else ""
        }, ensure_ascii=False) 