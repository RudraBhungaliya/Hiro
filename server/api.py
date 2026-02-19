from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import tempfile
import os
import shutil
from pathlib import Path
from models.parser import parse_file
from models.renderer import json_to_mermaid
from models.folder_parser import parse_folder
from models.github_parser import parse_github_repo, validate_github_url

app = FastAPI(
    title="HIRO API",
    description="AI-powered architectural diagram generator",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

class AnalyzeRequest(BaseModel):
    path: str
    mode: str = "auto"  # auto, file, folder, github

class AnalyzeResponse(BaseModel):
    mermaid: str
    description: str
    node_count: int
    edge_count: int
    success: bool

@app.get("/")
def root():
    return {
        "name": "HIRO API",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "POST /analyze": "Analyze project path and generate diagram",
            "GET /health": "Health check"
        }
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest):
    """
    Accepts a project path (file, folder, or GitHub URL).
    Returns mermaid diagram code + AI description + stats.
    """
    path_str = request.path.strip()
    
    if not path_str:
        raise HTTPException(status_code=400, detail="Path cannot be empty")

    diagram_data = {}
    
    try:
        # Detect mode if auto
        mode = request.mode
        if mode == "auto":
            if path_str.startswith(("http://", "https://")):
                mode = "github"
            elif os.path.isfile(path_str):
                mode = "file"
            elif os.path.isdir(path_str):
                mode = "folder"
            else:
                 raise HTTPException(status_code=400, detail=f"Path not found or invalid: {path_str}")

        print(f"Analyzing in {mode} mode: {path_str}")

        # Execute based on mode
        if mode == "github":
            if not validate_github_url(path_str):
                raise HTTPException(status_code=400, detail="Invalid GitHub URL")
            diagram_data = parse_github_repo(path_str)
            
        elif mode == "folder":
            if not os.path.exists(path_str):
                 raise HTTPException(status_code=404, detail="Folder not found")
            diagram_data = parse_folder(path_str)
            
        elif mode == "file":
             if not os.path.exists(path_str):
                 raise HTTPException(status_code=404, detail="File not found")
             diagram_data = parse_file(path_str)
             
        else:
             raise HTTPException(status_code=400, detail=f"Unknown mode: {mode}")

        mermaid_code = json_to_mermaid(diagram_data)
        description = diagram_data.get("description", "")
        nodes = diagram_data.get("nodes", [])
        if nodes is None:
            nodes = []
        edges = diagram_data.get("edges", [])
        if edges is None:
            edges = []

        return AnalyzeResponse(
            mermaid=mermaid_code,
            description=description,
            node_count=len(nodes),
            edge_count=len(edges),
            success=True
        )

    except Exception as e:
        print(f"Error analyzing {path_str}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
