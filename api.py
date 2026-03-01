from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import tempfile
import os
from pathlib import Path

from models.multi_language_parser import parse_file_any_language, parse_folder_multi_language
from models.multi_language_renderer import (
    build_mermaid_from_ai,
    build_description_from_ai,
    has_renderable_content,
)
from models.ai_engine import analyze_with_gemini
from models.github_parser import parse_github_repo, validate_github_url

app = FastAPI(
    title="HIRO API",
    description="AI-powered architectural diagram generator — converts any GitHub repo into a professional architecture diagram",
    version="3.0.0"
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
    mermaid:      str
    description:  str
    project_name: str
    project_type: str
    languages:    list
    file_count:   int
    node_count:   int
    edge_count:   int
    cached:       bool
    success:      bool
    error:        Optional[str] = None


# ── HELPERS ────────────────────────────────────────────────────────────

def facts_to_response(all_facts: dict) -> DiagramResponse:
    """
    Shared helper — runs AI engine and builds response.
    """
    has_any = any(
        has_renderable_content(f)
        for fl in all_facts.values()
        for f in fl
        if isinstance(f, dict)
    )
    if not has_any:
        raise HTTPException(
            status_code=422,
            detail="No analyzable structure found. "
                   "Make sure the repo contains .py, .java, .js, .ts, or .jsx files."
        )

    # Check if result will come from cache
    from models.ai_engine import build_facts_summary, compute_facts_hash, load_from_cache
    summary    = build_facts_summary(all_facts)
    facts_hash = compute_facts_hash(summary)
    is_cached  = load_from_cache(facts_hash) is not None

    ai_result    = analyze_with_gemini(all_facts)
    mermaid_code = build_mermaid_from_ai(ai_result)
    description  = build_description_from_ai(ai_result)

    project_name = ai_result.get("project_name", "Software Project")
    project_type = ai_result.get("project_type", "unknown")
    subgraphs    = ai_result.get("diagram", {}).get("subgraphs", [])
    edges        = ai_result.get("diagram", {}).get("edges", [])
    node_count   = sum(len(sg.get("nodes", [])) for sg in subgraphs)

    languages  = list(all_facts.keys())
    file_count = sum(len(fl) for fl in all_facts.values())

    return DiagramResponse(
        mermaid=mermaid_code,
        description=description,
        project_name=project_name,
        project_type=project_type,
        languages=languages,
        file_count=file_count,
        node_count=node_count,
        edge_count=len(edges),
        cached=is_cached,
        success=True
    )


# ── ROUTES ─────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "name":        "HIRO API",
        "version":     "3.0.0",
        "status":      "running",
        "description": "AI-powered architectural diagram generator",
        "endpoints": {
            "POST /analyze/github": "Analyze a GitHub repository by URL",
            "POST /analyze/code":   "Analyze a single file of code",
            "GET  /health":         "Health check",
            "GET  /cache/clear":    "Clear the diagram cache",
        },
        "supported_languages": [
            "Python (.py)",
            "Java (.java) — Spring Boot",
            "JavaScript (.js .jsx) — Node.js / Express / React",
            "TypeScript (.ts .tsx)",
        ]
    }


@app.get("/health")
def health():
    from models.ai_engine import CACHE_DIR
    cache_files = list(CACHE_DIR.glob("*.json"))
    return {
        "status":       "healthy",
        "version":      "3.0.0",
        "cache_entries": len(cache_files),
        "groq_model":   "llama-3.3-70b-versatile",
    }


@app.post("/analyze/github", response_model=DiagramResponse)
def analyze_github(request: AnalyzeGithubRequest):
    """
    Accepts a GitHub repository URL.
    Clones it, extracts architecture facts, sends to Groq AI,
    returns a professional subgraph Mermaid diagram + plain English description.

    Results are cached — same repo always returns same diagram instantly.

    Example:
        { "url": "https://github.com/expressjs/express" }
    """
    url = request.url.strip()

    if not url:
        raise HTTPException(
            status_code=400,
            detail="URL cannot be empty."
        )

    if not validate_github_url(url):
        raise HTTPException(
            status_code=400,
            detail="Invalid GitHub URL. Format: https://github.com/username/repository"
        )

    try:
        all_facts = parse_github_repo(url)

        if not all_facts:
            raise HTTPException(
                status_code=422,
                detail="No supported files found. "
                       "HIRO supports: .py, .java, .js, .jsx, .ts, .tsx"
            )

        return facts_to_response(all_facts)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@app.post("/analyze/code", response_model=DiagramResponse)
def analyze_code(request: AnalyzeCodeRequest):
    """
    Accepts raw source code as a string + a filename.
    Filename extension determines which language parser is used.
    Returns Mermaid diagram + plain English description.

    Example:
        { "code": "def hello(): pass", "filename": "app.py" }
    """
    if not request.code.strip():
        raise HTTPException(
            status_code=400,
            detail="Code cannot be empty."
        )

    suffix    = Path(request.filename).suffix.lower()
    supported = ['.py', '.java', '.js', '.jsx', '.ts', '.tsx']

    if not suffix:
        raise HTTPException(
            status_code=400,
            detail="Filename must have an extension e.g. app.py, Main.java, index.js"
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

        facts     = parse_file_any_language(tmp_path)
        language  = facts.get('language', 'unknown')
        all_facts = {language: [facts]}

        return facts_to_response(all_facts)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


@app.get("/cache/clear")
def clear_cache():
    """
    Clears all cached diagram results.
    Use this if you want to force fresh AI analysis for all repos.
    """
    from models.ai_engine import CACHE_DIR
    deleted = 0
    for cache_file in CACHE_DIR.glob("*.json"):
        try:
            cache_file.unlink()
            deleted += 1
        except Exception:
            pass
    return {
        "status":  "cleared",
        "deleted": deleted,
        "message": f"Removed {deleted} cached diagram(s)"
    }


@app.delete("/cache/{repo_hash}")
def clear_specific_cache(repo_hash: str):
    """
    Clears cache for a specific repo hash.
    Forces fresh AI analysis next time that repo is analyzed.
    """
    from models.ai_engine import CACHE_DIR
    cache_file = CACHE_DIR / f"{repo_hash}.json"
    if cache_file.exists():
        cache_file.unlink()
        return {"status": "cleared", "hash": repo_hash}
    raise HTTPException(
        status_code=404,
        detail=f"No cache found for hash: {repo_hash}"
    )


# ── RUN ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
