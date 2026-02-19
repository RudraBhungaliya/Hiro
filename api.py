from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import tempfile
import os
from pathlib import Path
from models.parser import parse_file
from models.renderer import json_to_mermaid

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
    code: str
    filename: str = "uploaded_code.py"


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
            "POST /analyze": "Analyze Python code and generate diagram",
            "GET /health": "Health check"
        }
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest):
    """
    Accepts raw Python code as a string.
    Returns mermaid diagram code + AI description + stats.
    """
    if not request.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty")

    if not request.filename.endswith(".py"):
        raise HTTPException(
            status_code=400,
            detail="Only Python files supported currently"
        )

    tmp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False
        ) as tmp:
            tmp.write(request.code)
            tmp_path = tmp.name

        diagram_data = parse_file(tmp_path)
        mermaid_code = json_to_mermaid(diagram_data)
        description = diagram_data.get("description", "")

        return AnalyzeResponse(
            mermaid=mermaid_code,
            description=description,
            node_count=len(diagram_data["nodes"]),
            edge_count=len(diagram_data["edges"]),
            success=True
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
