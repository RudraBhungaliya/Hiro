from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

from parser import parse_file
from folder_parser import parse_folder
from github_parser import parse_github_repo, validate_github_url
from renderer import json_to_mermaid

app = FastAPI()

class AnalyzeRequest(BaseModel):
    path: str
    mode: str = "auto"

@app.get("/")
def root():
    return {"status": "AI server running"}

@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    path_str = req.path.strip()

    if not path_str:
        raise HTTPException(status_code=400, detail="Path cannot be empty")

    try:
        mode = req.mode

        # Auto detect mode
        if mode == "auto":
            if path_str.startswith(("http://", "https://")):
                mode = "github"
            elif os.path.isfile(path_str):
                mode = "file"
            elif os.path.isdir(path_str):
                mode = "folder"
            else:
                raise HTTPException(status_code=400, detail="Invalid path")

        # Parse project
        if mode == "github":
            if not validate_github_url(path_str):
                raise HTTPException(status_code=400, detail="Invalid GitHub URL")
            diagram_data = parse_github_repo(path_str)

        elif mode == "folder":
            diagram_data = parse_folder(path_str)

        elif mode == "file":
            diagram_data = parse_file(path_str)

        else:
            raise HTTPException(status_code=400, detail="Unknown mode")

        mermaid_code = json_to_mermaid(diagram_data)

        nodes = diagram_data.get("nodes", [])
        edges = diagram_data.get("edges", [])

        return {
            "mermaid": mermaid_code,
            "description": diagram_data.get("description", "Generated diagram"),
            "node_count": len(nodes),
            "edge_count": len(edges),
            "success": True
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))