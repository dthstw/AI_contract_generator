from src.main import async_main
from src.search import search_txt_files
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from typing import List, Dict

load_dotenv()

app = FastAPI(title="AI Contract Generator", description="Generate professional contracts with AI assistance")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ContractRequest(BaseModel):
    contract_type: str
    number_of_words: int
    party_a: str
    party_b: str
    folder_to_save: str

class SearchRequest(BaseModel):
    query: str
    folder_to_search: str

@app.get("/")
async def read_root():
    """Serve the main HTML page"""
    return FileResponse("index.html")

@app.get("/health")
async def health_check():
    """Health check endpoint for Docker container"""
    return {
        "status": "healthy",
        "service": "AI Agent",
        "version": "1.0.0"
    }

@app.post("/contract")
async def contract(contract_request: ContractRequest):
    """Generate a contract based on the provided parameters"""
    return await async_main(contract_request)

@app.post("/search")
async def search(search_request: SearchRequest):
    """Search for contracts containing specific text"""
    try:
        if not os.path.exists(search_request.folder_to_search):
            raise HTTPException(status_code=404, detail=f"Folder '{search_request.folder_to_search}' not found")
        
        matching_files = search_txt_files(search_request.folder_to_search, search_request.query)
        
        # Get file details
        results = []
        for filename in matching_files:
            file_path = os.path.join(search_request.folder_to_search, filename)
            if os.path.exists(file_path):
                stat = os.stat(file_path)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Get a preview of the content around the search term
                    preview = get_content_preview(content, search_request.query)
                
                results.append({
                    "filename": filename,
                    "size": stat.st_size,
                    "modified": stat.st_mtime,
                    "preview": preview
                })
        
        return {
            "query": search_request.query,
            "folder": search_request.folder_to_search,
            "total_matches": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_content_preview(content: str, search_term: str, context_length: int = 150) -> str:
    """Get a preview of content around the search term"""
    lower_content = content.lower()
    lower_term = search_term.lower()
    
    index = lower_content.find(lower_term)
    if index == -1:
        return content[:context_length] + "..." if len(content) > context_length else content
    
    start = max(0, index - context_length // 2)
    end = min(len(content), index + len(search_term) + context_length // 2)
    
    preview = content[start:end]
    if start > 0:
        preview = "..." + preview
    if end < len(content):
        preview = preview + "..."
    
    return preview

@app.get("/contracts")
async def list_contracts(folder: str = "contracts"):
    """List all available contracts in a folder"""
    try:
        if not os.path.exists(folder):
            return {"contracts": [], "total": 0}
        
        contracts = []
        for filename in os.listdir(folder):
            if filename.endswith('.txt'):
                file_path = os.path.join(folder, filename)
                stat = os.stat(file_path)
                contracts.append({
                    "filename": filename,
                    "size": stat.st_size,
                    "modified": stat.st_mtime
                })
        
        # Sort by modification time (newest first)
        contracts.sort(key=lambda x: x['modified'], reverse=True)
        
        return {
            "contracts": contracts,
            "total": len(contracts),
            "folder": folder
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/contracts/{filename}")
async def get_contract(filename: str, folder: str = "contracts"):
    """Get the content of a specific contract"""
    try:
        file_path = os.path.join(folder, filename)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Contract not found")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        stat = os.stat(file_path)
        return {
            "filename": filename,
            "content": content,
            "size": stat.st_size,
            "modified": stat.st_mtime
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))