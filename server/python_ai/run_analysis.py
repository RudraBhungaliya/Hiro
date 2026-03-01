from fastapi import FastAPI
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

@app.get("/health")
def health():
    return {"status": "AI service running"}

@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    path_str = req.path.strip()
    mode = req.mode

    # Auto detect mode
    if mode == "auto":
        if path_str.startswith(("http://","https://")):
            mode = "github"
        elif os.path.isfile(path_str):
            mode = "file"
        elif os.path.isdir(path_str):
            mode = "folder"
        else:
            return {"success": False, "error": "Invalid path"}

    # Run analysis
    if mode == "github":
        diagram_data = parse_github_repo(path_str)
    elif mode == "folder":
        diagram_data = parse_folder(path_str)
    else:
        diagram_data = parse_file(path_str)

    mermaid_code = json_to_mermaid(diagram_data)

    return {
        "success": True,
        "mermaid": mermaid_code,
        "description": diagram_data.get("description",""),
        "node_count": len(diagram_data.get("nodes",[])),
        "edge_count": len(diagram_data.get("edges",[]))
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=9000)