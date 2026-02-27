from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import tempfile
import os
from pathlib import Path

from models.multi_language_parser import parse_file_any_language, parse_folder_multi_language
from models.multi_language_renderer import (
    build_mermaid_multi_language,
    generate_description,
    detect_cross_language_dependencies,
    has_renderable_content
)
from models.github_parser import parse_github_repo, validate_github_url

app = FastAPI(
    title="HIRO API",
    description="AI-powered architectural diagram generator — supports Python, Java, JavaScript, TypeScript, React, HTML, CSS",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


# ── REQUEST / RESPONSE MODELS ──────────────────────────────────────────

class AnalyzeCodeRequest(BaseModel):
    code: str
    filename: str = "uploaded_code.py"


class AnalyzeGithubRequest(BaseModel):
    url: str


class DiagramResponse(BaseModel):
    mermaid: str
    description: str
    languages: list
    file_count: int
    node_count: int
    edge_count: int
    success: bool
    error: Optional[str] = None


# ── HELPERS ────────────────────────────────────────────────────────────

def facts_to_response(all_facts: dict) -> DiagramResponse:
    """
    Convert all_facts dict into a DiagramResponse.
    Shared by all endpoints.
    """
    cross_deps   = detect_cross_language_dependencies(all_facts)
    mermaid_code = build_mermaid_multi_language(all_facts)
    description  = generate_description(all_facts, cross_deps)

    # Count nodes and edges from mermaid output
    lines      = mermaid_code.split('\n')
    node_lines = [l for l in lines if '[' in l or '((' in l and '%%' not in l]
    edge_lines = [l for l in lines if '-->' in l]

    languages  = list(all_facts.keys())
    file_count = sum(len(fl) for fl in all_facts.values())

    return DiagramResponse(
        mermaid=mermaid_code,
        description=description,
        languages=languages,
        file_count=file_count,
        node_count=len(node_lines),
        edge_count=len(edge_lines),
        success=True
    )


# ── ROUTES ─────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "name": "HIRO API",
        "version": "2.0.0",
        "status": "running",
        "endpoints": {
            "POST /analyze/code":   "Analyze a single file of code (paste code as string)",
            "POST /analyze/github": "Analyze a GitHub repository by URL",
            "GET  /health":         "Health check"
        },
        "supported_languages": [
            "Python (.py)",
            "Java (.java) — Spring Boot",
            "JavaScript (.js, .jsx) — Node.js / React",
            "TypeScript (.ts, .tsx)",
            "HTML (.html)",
            "CSS (.css)"
        ]
    }


@app.get("/health")
def health():
    return {"status": "healthy", "version": "2.0.0"}


@app.post("/analyze/code", response_model=DiagramResponse)
def analyze_code(request: AnalyzeCodeRequest):
    """
    Accepts raw source code as a string + a filename.
    Filename determines which language parser is used.
    Returns Mermaid diagram + plain English description.

    Example:
        {
            "code": "def hello(): pass",
            "filename": "app.py"
        }
    """
    if not request.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty.")

    suffix = Path(request.filename).suffix.lower()
    supported = ['.py', '.java', '.js', '.jsx', '.ts', '.tsx', '.html', '.css']

    if not suffix:
        raise HTTPException(
            status_code=400,
            detail="Filename must have an extension. Example: app.py, Main.java, index.html"
        )

    if suffix not in supported:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{suffix}'. Supported: {', '.join(supported)}"
        )

    tmp_path = None

    try:
        stem = Path(request.filename).stem
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=suffix,
            prefix=stem + "_",
            delete=False
        ) as tmp:
            tmp.write(request.code)
            tmp_path = tmp.name

        facts    = parse_file_any_language(tmp_path)
        language = facts.get('language', 'unknown')
        all_facts = {language: [facts]}

        return facts_to_response(all_facts)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


@app.post("/analyze/github", response_model=DiagramResponse)
def analyze_github(request: AnalyzeGithubRequest):
    """
    Accepts a GitHub repository URL.
    Clones it, analyzes all supported files, returns diagram + description.

    Example:
        {
            "url": "https://github.com/expressjs/express"
        }
    """
    url = request.url.strip()

    if not url:
        raise HTTPException(status_code=400, detail="URL cannot be empty.")

    if not validate_github_url(url):
        raise HTTPException(
            status_code=400,
            detail="Invalid GitHub URL. Format must be: https://github.com/username/repository"
        )

    try:
        all_facts = parse_github_repo(url)

        if not all_facts:
            raise HTTPException(
                status_code=422,
                detail="Repository was cloned but no supported files were found. "
                       "HIRO supports: .py, .java, .js, .jsx, .ts, .tsx, .html, .css"
            )

        # Check if anything actually has content
        has_any_content = any(
            has_renderable_content(f)
            for fl in all_facts.values()
            for f in fl
            if isinstance(f, dict)
        )

        if not has_any_content:
            raise HTTPException(
                status_code=422,
                detail="Files were found but no analyzable structure detected. "
                       "The repository may use unsupported patterns."
            )

        return facts_to_response(all_facts)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


# ── RUN ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)