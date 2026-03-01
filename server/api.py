from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

from models.parser import parse_file
from models.renderer import json_to_mermaid
from models.folder_parser import parse_folder
from models.github_parser import parse_github_repo, validate_github_url


app = FastAPI(
    title="HIRO API",
    description="AI-powered architectural diagram generator",
    version="1.0.0"
)

# CORS (allow frontend to call backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Request / Response Models ----------

class AnalyzeRequest(BaseModel):
    path: str
    mode: str = "auto"   # auto | file | folder | github


class AnalyzeResponse(BaseModel):
    mermaid: str
    description: str
    node_count: int
    edge_count: int
    success: bool


# ---------- Health Routes ----------

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


# ---------- MAIN ANALYZE ENDPOINT ----------

@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest):
    """
    Accepts:
      - Local file path
      - Local folder path
      - GitHub repo URL

    Returns:
      - Mermaid diagram code
      - Description
      - Node & edge stats
    """

    path_str = request.path.strip()

    if not path_str:
        raise HTTPException(status_code=400, detail="Path cannot be empty")

    try:
        # ---------- Auto detect mode ----------
        mode = request.mode

        if mode == "auto":
            if path_str.startswith(("http://", "https://")):
                mode = "github"
            elif os.path.isfile(path_str):
                mode = "file"
            elif os.path.isdir(path_str):
                mode = "folder"
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Path not found or invalid: {path_str}"
                )

        print(f"🔎 Analyzing in {mode} mode: {path_str}")

        # ---------- Parse project ----------
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

        # ---------- Convert JSON → Mermaid ----------
        mermaid_code = json_to_mermaid(diagram_data)

        # ---------- Extract metadata safely ----------
        description = diagram_data.get("description", "Project architecture diagram")
        nodes = diagram_data.get("nodes", []) or []
        edges = diagram_data.get("edges", []) or []

        print(f"✅ Generated diagram: {len(nodes)} nodes, {len(edges)} edges")

        # ---------- Final response ----------
        return AnalyzeResponse(
            mermaid=mermaid_code,
            description=description,
            node_count=len(nodes),
            edge_count=len(edges),
            success=True
        )

    except Exception as e:
        print(f"❌ Error analyzing {path_str}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


# ---------- Run locally ----------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)